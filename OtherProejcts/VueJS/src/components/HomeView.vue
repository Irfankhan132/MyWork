<template>
    <h1>Home Component of Irfan's life and many happiness, like more than {{ 10 + 10 }}. The length of hello is  {{ "Holle".length }}</h1>
    <h1>Email {{ email }}</h1>
    <h1>FirstName: {{ getName("Irfan ullah") }}</h1>
    <h1>LastName: {{ getName("Khan") }}</h1>
    <!-- <h1>Wife's data: {{ getData() }}</h1> -->
    <button v-on:click="getData('Button 1 click')">Click Me</button>
    <h2>{{ count }}</h2>
    <!-- <Child name2="Parent Child Component Example." :user="user"/> -->

</template>
<script>
// import Child from './ParentChildComponent.vue'
export default{
    name:'HomeView',
    data()
    {
        return {
            count:0,
            //user:{name:'Numan',email:'numan@gmail.com'}
        }
    },



    // data(){
    //     return{
    //         email:'irfanee125@gmail.com',
                       
    
    //     }
    // },
    methods:{
        getName(name){
            return name;
        },
        getData()
        {
            this.count = this.count+2;
        },
        // getConsole()
        // {
        //     console.warn("Function called")
        // }
    },
    // components:{
    //     Child
    // }
    

}
</script>

<style scoped>

h1{
    color: orange;
}

h2{
    color: aquamarine;
}
</style>