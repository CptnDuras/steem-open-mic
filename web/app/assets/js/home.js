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
            var test_videos = [{
                title: "Awesome video 1!",
                source: "https://youtu.be/2Sv9DfZO0ow",
                img: "https://www.fillmurray.com/300/300",
                description: "1 This is a really awesome video you should watch",
                duration: "03:15"
            },{
                title: "Awesome video 2!",
                source: "https://youtu.be/2Sv9DfZO0ow",
                img: "https://www.fillmurray.com/300/300",
                description: "2 This is a really awesome video you should watch",
                duration: "03:15"
            },{
                title: "Awesome video 3!",
                source: "https://youtu.be/2Sv9DfZO0ow",
                img: "https://www.fillmurray.com/300/300",
                description: "3 This is a really awesome video you should watch",
                duration: "03:15"
            },{
                title: "Awesome video 4!",
                source: "https://youtu.be/2Sv9DfZO0ow",
                img: "https://www.fillmurray.com/300/300",
                description: "4 This is a really awesome video you should watch",
                duration: "03:15"
            },{
                title: "Awesome video 5!",
                source: "https://youtu.be/2Sv9DfZO0ow",
                img: "https://www.fillmurray.com/300/300",
                description: "5 This is a really awesome video you should watch",
                duration: "03:15"
            },{
                title: "Awesome video 6!",
                source: "https://www.fillmurray.com/300/300",
                img: "http://i.ytimg.com/vi/ZKOtE9DOwGE/mqdefault.jpg",
                description: "6 This is a really awesome video you should watch",
                duration: "03:15"
            }];
            var self = this;

            test_videos.forEach(function (video) {
                self.addSlide(video);
            });
        },
        addSlide(video){
            var video_tile = '' +
                '<a href="#" title="' + video.title + '">\n' +
                '    <img data-lazy="' + video.img + '" alt="' + video.title + '" class="img-responsive" height="130px" />\n' +
                '    <h2>' + video.description + '</h2>\n' +
                '    <span class="glyphicon glyphicon-play-circle"></span>\n' +
                '    <span class="duration">' + video.duration + '</span>\n' +
                '</a>';
            this.carousels.slick(
                'slickAdd',
                video_tile
            )
        }
    }

});

/*
* this is what i want the template to look like
<a href="#" title="' + video.title + '">
    <img data-lazy="' + video.img + '" alt="' + video.title + '" class="img-responsive" height="130px" />
    <h2>' + video.description + '</h2>
    <span class="glyphicon glyphicon-play-circle"></span>
    <span class="duration">' + video.duration + '</span>
</a>
* */