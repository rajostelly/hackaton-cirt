// https://reactrouter.com/start/framework/routing
import { createBrowserRouter } from "react-router-dom";
import { Dashboard } from "@/features/dashboard/components/Dashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Dashboard />,
  },
]);
