var player = Vue.component(
    "player",
    {
        data() {
            return {
                width: 160,
                height: 90
            }
        },
        props: ["video"],
        template: "#player",
        updated() {
            this.resize();
        },
        mounted() {
            // stuff here
            this.resize();
        },
        methods: {
            resize() {
                if (window.innerWidth  / 1.2 <= 800) {
                    this.width = window.innerWidth / 1.2;
                    this.height = this.width / (16 / 9);
                } else {
                    this.width = 800;
                    this.height = 800 / (16 / 9);
                }
            }
        }

    }
);