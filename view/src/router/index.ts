import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import CreatingVNet from "../views/CreatingVNet.vue";
import TracingPacket from "../views/TracingPacket.vue";
import TracingVNet from "../views/TracingVNet.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "VNet",
    component: CreatingVNet,
    // props: {
    //   "vnet": vnet
    // }
  },
  {
    path: "/tracing_net",
    name: "tracing_net",
    component: TracingVNet
  },
  {
    path: "/tracing_packet",
    name: "trace_packet",
    component: TracingPacket,
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
