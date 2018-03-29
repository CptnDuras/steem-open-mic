var home = Vue.component("home", {
    template: "#home",
    data(){
        return {
            api_url: "/api/hot/videos",
            hot_videos: [],
            current_video: null,
            player_show: false,
            slick_config: {
                slidesToShow: 4,
                slidesToScroll: 4,
                infinite: false,
                responsive: [
                    {
                        breakpoint: 1024,
                        settings: {
                            slidesToShow: 3,
                            slidesToScroll: 3,
                        }
                    },
                    {
                        breakpoint: 600,
                        settings: {
                            slidesToShow: 2,
                            slidesToScroll: 2
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }
                ]
            },
            carousels: $('.carousel'),
        }
    },
    ready(){
        // this.setupCarousels();
    },
    updated(){
        if($(".slick-track").children().length == 0){
            this.destroyCarousels();
            this.setupCarousels();
        }

    },
    mounted(){
        console.log("home was added");
        this.carousels = $('.carousel');
        this.getVideos();

        // this.setupCarousels();
        // var self = this;
        //
        // this.carousels.on('breakpoint', function(slick) {
        //     self.destroyCarousels();
        //     self.setupCarousels();
        // });

        this.setupCarousels();
    },
    methods: {
        setupCarousels(){
            this.carousels.slick(this.slick_config);
        },
        destroyCarousels(){
            this.carousels.slick('unslick');
        },
        getVideos(){
            // Go and get the videos from the API
            var self = this;

            $.ajax({
                url: self.api_url,
                method: "GET",
            }).done(function(data){
                var hot_videos = [];

                data.forEach(function(item){
                    var new_item = self.addVideoMeta(item);
                    hot_videos.push(new_item);
                });

                console.log(hot_videos);
                self.hot_videos = hot_videos;
            });
        },
        addVideoMeta(video){
            var img = "";
            var url = "";

            if(video.video_type === "dtube"){
                url = 'https://d.tube/#!/v/' + video.author + '/' + video.permlink;
                img = "/static/img/dtube-icon.png";
            }else if(video.video_type === "dlive"){
                img = "/static/img/dlive-icon.png";

                if(video.video_id === 'live') {
                    url = 'https://www.dlive.io/#/livestream/' + video.author + '/' + video.permlink;
                }else{
                    url = 'https://www.dlive.io/#/video/' + video.author + '/' + video.permlink;
                }
            }else if(video.video_type === "youtube"){
                // url = 'https://www.youtube.com/watch?v=' + video.video_id;
                url = 'https://www.youtube.com/embed/' + video.video_id + '?autoplay=1';
                img = "https://img.youtube.com/vi/" + video.video_id + "/0.jpg";
            }

            video.upload_time = new Date(video.created);
            video.url = url;
            video.img = img;
            video.mode = "video_tile";
            video.play_video = this.play_video;
            video.close_video = this.close_video;

            return video;
        },
        play_video(video){
            this.player_show = true;
            this.current_video = video;
        },
        close_video(video){
            this.player_show = false;
            this.current_video =  null;
        }
    }

});

