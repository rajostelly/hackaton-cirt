import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/shared/layout/AppLayout";
import { Dashboard } from "@/features/dashboard/components/Dashboard";
import { AlertsPage } from "@/features/alerts/components/AlertsPage";
import { ScansPage } from "@/features/scans/components/ScansPage";
import { IntegrationsPage } from "@/features/integrations/components/IntegrationsPage";
import { SettingsPage } from "@/features/settings/components/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "alerts", element: <AlertsPage /> },
      { path: "scans", element: <ScansPage /> },
      { path: "integrations", element: <IntegrationsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
