<template>
    <h2>How to pass value in child component from parent component</h2>
    <h2>{{ name2 }}</h2>
    <h2>{{ user.name }}</h2>
    <h2>{{ user.email }}</h2>
</template>

<script>

// 1. Make CHild Component.
// 2. Import and use CHild Component
// 3. Pass Static Data
// 4. Pass Property, object, and function to child Component

export default{

    name: "ParentChildComponent",
    props:{
        name2:String,
        user:Object
    }

}


</script>

<style>
h1{

    color: brown;
}


</style>