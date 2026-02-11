import DetailLawyer from "../components/detailLawyer.vue";
import ListLawyers from "../components/ListLawyers.vue";
import {createRouter,createWebHashHistory} from 'vue-router'
const routes = [
    {path:'/', name:'Accueil', component:ListLawyers},
    {path:'/lawyer/:id', name:'Détail', component:DetailLawyer}
],
    router = createRouter({
        history:createWebHashHistory(),
        routes
    })
export default router;