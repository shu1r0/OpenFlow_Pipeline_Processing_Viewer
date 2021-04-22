import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import CreatingVNet from "../views/CreatingVNet.vue";
import TracePacket from "../views/TracePacket.vue"

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "VNet",
    component: CreatingVNet,
  },
  {
    path: "/trace",
    name: "trace",
    component: TracePacket,
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
