<template>
    <h1>Two way binding</h1>
    <input type="" v-model="count"/>

    <h2>{{ count }}</h2>
</template>

<script>

export default {
    name: "TwoWayBinding",
    data()
    {
        return{
            count:0
        }
    }

}

</script>

<style scoped>

h1{
    color: orange;
}

</style>