var ui = Vue.component("ui", {
    template: "#ui",
    data: ()=>({
        stuff: []
    }),
    mounted(){
        console.log("ui was added");
        this.doStuff();
    },
    methods: {
        doStuff(){
            // Go and get the videos from the API
        }
    }

});