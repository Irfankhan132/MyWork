<template>
<img alt="Vue logo" src="./assets/logo.png">
<HelloWorld msg="Welcome to Irfan's life with a lot of success, fauiler, struggle and achivement" />
<HomeView />
<TwoWayBinding />
<GetInputValues />
<CheckboxRadio />
<IfElse />
<ParentChildComponent />

</template>

<script>
import CheckboxRadio from './components/CheckboxRadio.vue';
import GetInputValues from './components/GetInputValues.vue';
import HelloWorld from './components/HelloWorld.vue'
import HomeView from './components/HomeView.vue'
import IfElse from './components/ifElse.vue';
import ParentChildComponent from './components/ParentChildComponent.vue';
import TwoWayBinding from './components/TwoWayBinding.vue'


export default {
    name: 'App',
    components: {
        HelloWorld,
        HomeView,
        TwoWayBinding,
        GetInputValues,
        CheckboxRadio,
        IfElse,
        ParentChildComponent,
    }
}
</script>

<style>

</style>
