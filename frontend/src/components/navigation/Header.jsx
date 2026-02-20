import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import Icon from "../AppIcon";

const Header = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [configProgress, setConfigProgress] = useState(false);

  useEffect(() => {
    const configComplete = localStorage.getItem("pilotarr_config_complete");
    setConfigProgress(!configComplete);
  }, []);

  const navigationItems = [
    {
      label: "Dashboard",
      path: "/main-dashboard",
      icon: "LayoutDashboard",
      tooltip: "Unified monitoring hub",
    },
    {
      label: "Library",
      path: "/library",
      icon: "Library",
      tooltip: "Browse media collection",
    },
    {
      label: "Monitoring",
      path: "/monitoring",
      icon: "Monitor",
      tooltip: "Sonarr/Radarr media tracking",
    },
    {
      label: "Analytics",
      path: "/jellyfin-statistics",
      icon: "BarChart3",
      tooltip: "Detailed usage statistics",
    },
    {
      label: "Torrents",
      path: "/torrents",
      icon: "Download",
      tooltip: "Torrent client management",
    },
    {
      label: "Calendar",
      path: "/calendar",
      icon: "Calendar",
      tooltip: "Media release schedule and activity",
    },
    {
      label: "Configuration",
      path: "/initial-configuration",
      icon: "Settings",
      tooltip: "API setup and service connections",
    },
  ];

  const isActive = (path) => location?.pathname === path;

  const toggleMobileMenu = () => setIsMobileMenuOpen((prev) => !prev);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  useEffect(() => {
    document.body.style.overflow = isMobileMenuOpen ? "hidden" : "unset";
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      <header className="nav-header">
        <div className="nav-header-container">
          <div className="nav-header-logo">
            <div className="nav-header-logo-icon">
              <Icon name="Server" size={24} color="var(--color-primary)" />
            </div>
            <span className="nav-header-logo-text">Pilotarr</span>
          </div>

          <nav className="nav-header-menu">
            {navigationItems?.map((item) => (
              <Link
                key={item?.path}
                to={item?.path}
                className={`nav-header-item ${isActive(item?.path) ? "active" : ""}`}
                title={item?.tooltip}
              >
                <Icon name={item?.icon} size={18} className="mr-2" />
                {item?.label}
                {item?.path === "/initial-configuration" && configProgress && (
                  <span className="progress-badge">!</span>
                )}
              </Link>
            ))}
          </nav>

          {/* Mobile hamburger — hidden on lg+ */}
          <button
            className="lg:hidden flex items-center justify-center w-10 h-10 rounded-lg hover:bg-muted transition-colors"
            onClick={toggleMobileMenu}
            aria-label="Toggle mobile menu"
            aria-expanded={isMobileMenuOpen}
          >
            <Icon name={isMobileMenuOpen ? "X" : "Menu"} size={22} />
          </button>
        </div>
      </header>

      {/* Mobile overlay menu */}
      <div className={`nav-mobile-menu ${!isMobileMenuOpen ? "closed" : ""}`}>
        <div className="nav-mobile-menu-header">
          <div className="nav-header-logo">
            <div className="nav-header-logo-icon">
              <Icon name="Server" size={24} color="var(--color-primary)" />
            </div>
            <span className="nav-header-logo-text">Pilotarr</span>
          </div>
        </div>

        <nav className="nav-mobile-menu-items">
          {navigationItems?.map((item) => (
            <Link
              key={item?.path}
              to={item?.path}
              className={`nav-mobile-menu-item ${isActive(item?.path) ? "active" : ""}`}
              onClick={closeMobileMenu}
            >
              <Icon name={item?.icon} size={20} className="mr-3" />
              {item?.label}
              {item?.path === "/initial-configuration" && configProgress && (
                <span className="progress-badge">!</span>
              )}
            </Link>
          ))}
        </nav>
      </div>
    </>
  );
};

export default Header;
