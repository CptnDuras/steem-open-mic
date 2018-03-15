var home = Vue.component("home", {
    template: "#home",
    data: ()=>({
        stuff: []
    }),
    mounted(){
        console.log("home was added");
        this.getVideos();
    },
    methods: {
        getVideos(){
            // Go and get the videos from the API
        }
    }

});