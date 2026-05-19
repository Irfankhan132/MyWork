<template>
    <h1>Check box and radio button</h1>
    <h3>technology</h3>
    <label for="java">Java</label>
    <input type="checkbox" value="java" v-model="technology" id="java">
    <br>


    <label for="PhP">PhP</label>
    <input type="checkbox" value="PhP" v-model="technology" id="PhP">
    <br>

    <label for="C++">C++</label>
    <input type="checkbox" value="C++" v-model="technology" id="C++">
    <br> <br>

    <h3>Who I am</h3>

    <label for="student">student</label>
    <input type="radio" value="student" v-model="who" name="profession" id="student"> <br>

    <label for="developer">developer</label>
    <input type="radio" value="developer" v-model="who" name="profession" id="developer">

    <br> <br>



    <h4>Selected technologies {{ technology }} </h4>
    <h4>I am a : {{ who }}</h4>
</template>

<script>

export default{
    name: "CheckboxRadio",
    data(){
        return{
            technology:[],
            who:null,
        }
    }
}


</script>

<style scoped>

h1{

    color: blueviolet;

}

</style>