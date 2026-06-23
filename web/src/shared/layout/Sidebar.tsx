import { NavLink, useMatch } from "react-router-dom";
import {
  LayoutDashboard,
  Bell,
  Radar,
  Plug2,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldCheck,
} from "lucide-react";

type IconComponent = React.ComponentType<{ className?: string }>;

interface NavItemDef {
  to: string;
  icon: IconComponent;
  label: string;
  end?: boolean;
}

const NAV_ITEMS: NavItemDef[] = [
  { to: "/",            icon: LayoutDashboard, label: "Vue d'ensemble",  end: true },
  { to: "/alerts",      icon: Bell,            label: "Alertes" },
  { to: "/scans",       icon: Radar,           label: "Détections" },
  { to: "/integrations",icon: Plug2,           label: "Intégrations" },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`${
        collapsed ? "w-[60px]" : "w-56"
      } shrink-0 transition-[width] duration-200 ease-in-out bg-surface-alt border-r border-gray-800/80 flex flex-col`}
    >
      {/* Brand */}
      <div
        className={`h-14 flex items-center border-b border-gray-800/80 shrink-0 ${
          collapsed ? "justify-center px-3" : "px-4 gap-3"
        }`}
      >
        <ShieldCheck className="w-5 h-5 text-blue-500 shrink-0" />
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm text-white leading-tight">ARO SOC</p>
            <p className="text-xs text-gray-600 leading-tight">Security Operations</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className={`text-gray-600 hover:text-gray-300 p-1.5 rounded transition-colors ${
            collapsed ? "mt-0" : "ml-auto"
          }`}
          aria-label={collapsed ? "Ouvrir" : "Réduire"}
        >
          {collapsed ? (
            <PanelLeftOpen className="w-3.5 h-3.5" />
          ) : (
            <PanelLeftClose className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 flex flex-col gap-px px-2 overflow-hidden">
        {!collapsed && (
          <p className="px-2 mb-1 text-[10px] font-semibold text-gray-700 uppercase tracking-widest select-none">
            Menu
          </p>
        )}
        {NAV_ITEMS.map((item) => (
          <SidebarNavItem key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Bottom */}
      <div className="py-3 px-2 border-t border-gray-800/80 shrink-0">
        <SidebarNavItem
          item={{ to: "/settings", icon: Settings, label: "Paramètres" }}
          collapsed={collapsed}
        />
      </div>
    </aside>
  );
}

/* ── NavItem uses useMatch so we can conditionally render the indicator ── */
function SidebarNavItem({
  item: { to, icon: Icon, label, end },
  collapsed,
}: {
  item: NavItemDef;
  collapsed: boolean;
}) {
  const match = useMatch({ path: to, end: end ?? false });
  const isActive = Boolean(match);

  return (
    <NavLink
      to={to}
      end={end}
      title={collapsed ? label : undefined}
      className={`
        relative flex items-center gap-3 rounded-md text-sm font-medium
        transition-colors select-none
        ${collapsed ? "justify-center px-2 py-2.5" : "px-3 py-2"}
        ${
          isActive
            ? "bg-surface-elevated text-white"
            : "text-gray-500 hover:text-gray-200 hover:bg-surface-elevated/60"
        }
      `}
    >
      {/* Left indicator */}
      {isActive && (
        <span className="absolute left-0 top-1.5 bottom-1.5 w-[2px] bg-blue-500 rounded-r-full" />
      )}

      <Icon
        className={`w-4 h-4 shrink-0 ${isActive ? "text-blue-400" : ""}`}
      />
      {!collapsed && (
        <span className="truncate leading-none">{label}</span>
      )}
    </NavLink>
  );
}
