<template>

    <h1 v-if="show">IF condition</h1>
    <h1 v-else>Else condition</h1>
    <button v-on:click="show=!show">Toogle</button>

</template>

<script>

    export default{
        name:"ifElse",

        data(){
            return{
                show:true
            }
        }
    }

</script>


<style scoped>
h1{
    color: brown;
}

</style>