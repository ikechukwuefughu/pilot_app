document.addEventListener('DOMContentLoaded', function () {
    const submenuItems = document.querySelectorAll('.has-submenu');

    submenuItems.forEach(item => {
        const trigger = item.querySelector(':scope > a');

        trigger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            // Close all other submenus
            submenuItems.forEach(other => {
                if (other !== item) {
                    other.classList.remove('open');
                }
            });

            // Toggle current submenu
            item.classList.toggle('open');
        });
    });

    // Close all when clicking outside sidebar
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.sidebar')) {
            submenuItems.forEach(item => {
                item.classList.remove('open');
            });
        }
    });

    // Close submenus when clicking a normal menu item
    document.querySelectorAll('.sidebar-menu > li:not(.has-submenu) > a')
        .forEach(link => {
            link.addEventListener('click', function () {
                submenuItems.forEach(item => {
                    item.classList.remove('open');
                });
            });
        });
});