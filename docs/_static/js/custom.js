// Custom JavaScript for RoboRacer documentation
document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.querySelector('.wy-nav-side');

    if (!sidebar) {
        return;
    }

    var toggle = document.createElement('button');
    toggle.className = 'sidebar-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-controls', 'wy-side-navigation');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Hide navigation');
    toggle.title = 'Hide navigation';

    for (var line = 0; line < 3; line += 1) {
        var bar = document.createElement('span');
        bar.className = 'sidebar-toggle-line';
        toggle.appendChild(bar);
    }

    var navigation = sidebar.querySelector('.wy-menu-vertical');
    if (navigation) {
        navigation.id = 'wy-side-navigation';
    }

    function setSidebarCollapsed(isCollapsed) {
        document.body.classList.toggle('sidebar-collapsed', isCollapsed);
        toggle.setAttribute('aria-expanded', String(!isCollapsed));
        toggle.setAttribute('aria-label', isCollapsed ? 'Show navigation' : 'Hide navigation');
        toggle.title = isCollapsed ? 'Show navigation' : 'Hide navigation';
    }

    toggle.addEventListener('click', function () {
        setSidebarCollapsed(!document.body.classList.contains('sidebar-collapsed'));
    });

    var rail = document.createElement('nav');
    rail.className = 'sidebar-rail';
    rail.setAttribute('aria-label', 'Collapsed navigation');

    function addRailButton(icon, label, action) {
        var button = document.createElement('button');
        var iconElement = document.createElement('span');

        button.className = 'sidebar-rail-button';
        button.type = 'button';
        button.setAttribute('aria-label', label);
        button.title = label;
        iconElement.className = 'fa ' + icon;
        iconElement.setAttribute('aria-hidden', 'true');
        button.appendChild(iconElement);
        button.addEventListener('click', action);
        rail.appendChild(button);
    }

    addRailButton('fa-search', 'Open navigation and search', function () {
        setSidebarCollapsed(false);
        var search = sidebar.querySelector('input[type="text"]');
        if (search) {
            search.focus();
        }
    });

    addRailButton('fa-book', 'Open Modules navigation', function () {
        setSidebarCollapsed(false);
        var firstModule = navigation.querySelector('a.toctree-l1');
        if (firstModule) {
            firstModule.focus();
        }
    });

    addRailButton('fa-wrench', 'Open Build/Repair Manual', function () {
        var manual = navigation.querySelector('a[href*="robot-build-manual"]');
        if (manual) {
            window.location.href = manual.href;
        } else {
            setSidebarCollapsed(false);
        }
    });

    document.body.appendChild(rail);
    document.body.appendChild(toggle);
});
