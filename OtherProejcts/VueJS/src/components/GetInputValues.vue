<template>
    <h1>Get Input field value</h1>
    <input type="text" placeholder="enter email" v-model="email"/>
    <br />
    <br />
    <input type="text" placeholder="password" v-model="password"/>
    <br />
    <br />
    <button v-on:click="getData()" type="button">Get values</button>
</template>

<script>

export default{
    name: "GetInputValues",
    data(){
        return{
            email:null,
            password:null,
        }
    },
    methods:{

        getData(){

            console.warn("values: ", this.email, this.password)

        }

    }
}

</script>

<style>
 h1{
    color: black;
 }
</style>