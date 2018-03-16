var home = Vue.component("home", {
    template: "#home",
    data: ()=>({
        stuff: []
    }),
    mounted(){
        console.log("home was added");
        this.carousels = $('.carousel');

        this.slick_config = {
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
        };

        this.setupCarousels();
        var self = this;

        this.carousels.on('breakpoint', function(slick) {
            self.destroyCarousels();
            self.setupCarousels();
        });

        this.getVideos();
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
                url: "/api/hot/videos",
                method: "GET",

            }).done(function(data){
                console.log(data);
                data.forEach(function (video) {
                    self.addSlide(video);
                });
            });
        },
        addSlide(video){
            var img = "";
            var url = "";

            if(video.video_type == "dtube"){
                url = 'https://d.tube/#!/v/' + video.author + '/' + video.permlink;
                img = "/static/img/dtube-icon.png";
            }else if(video.video_type == "dlive"){
                img = "/static/img/dlive-icon.png";

                if(video.video_id == 'live') {
                    url = 'https://www.dlive.io/#/livestream/' + video.author + '/' + video.permlink;
                }else{
                    url = 'https://www.dlive.io/#/video/' + video.author + '/' + video.permlink;
                }
            }else if(video.video_type == "youtube"){
                url = 'https://www.youtube.com/watch?v=' + video.video_id;
                img = "https://img.youtube.com/vi/" + video.video_id + "/0.jpg";
            }

            var upload_time = new Date(video.created * 1000);

            var video_tile = '' +
                '<a href="#" title="' + video.title + '">\n' +
                '    <img data-lazy="' + img + '" alt="' + video.title + '" class="img-responsive" height="130px" />\n' +
                '    <h4>' + video.title_truncated + '...</h4>\n' +
                '    <span class="glyphicon glyphicon-play-circle"></span>\n' +
                '    <span class="upload">' + upload_time + '</span>\n' +
                '</a>';

            this.carousels.slick(
                'slickAdd',
                video_tile
            )
        }
    }

});