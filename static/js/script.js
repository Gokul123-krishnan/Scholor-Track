/**
 * Scholar Track - Scholarship Management System
 * Front-end interactivity: Mobile drawer, Delete confirmation modal,
 * Status quick-changes, and Flash alert auto-dismissal.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Navigation Toggle
  const sidebar = document.getElementById('appSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const sidebarClose = document.getElementById('sidebarClose');

  function openSidebar() {
    if (sidebar && sidebarOverlay) {
      sidebar.classList.add('show');
      sidebarOverlay.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeSidebar() {
    if (sidebar && sidebarOverlay) {
      sidebar.classList.remove('show');
      sidebarOverlay.classList.remove('show');
      document.body.style.overflow = '';
    }
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', openSidebar);
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }

  if (sidebarClose) {
    sidebarClose.addEventListener('click', closeSidebar);
  }

  // 2. Global Delete Confirmation Modal Handler
  const deleteModalEl = document.getElementById('deleteConfirmModal');
  if (deleteModalEl) {
    deleteModalEl.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      const button = event.relatedTarget;
      if (!button) return;

      const scholarshipId = button.getAttribute('data-scholarship-id');
      const scholarshipName = button.getAttribute('data-scholarship-name');

      const modalTitleEl = deleteModalEl.querySelector('#deleteModalScholarshipName');
      const formEl = deleteModalEl.querySelector('#deleteScholarshipForm');

      if (modalTitleEl) {
        modalTitleEl.textContent = scholarshipName || 'this scholarship';
      }

      if (formEl) {
        formEl.action = `/scholarships/${scholarshipId}/delete`;
      }
    });
  }

  // 3. Auto-dismiss Flash Alerts after 5 seconds
  const flashAlerts = document.querySelectorAll('.alert-dismissible');
  flashAlerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {
        // Fallback for older browsers
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
      }
    }, 5000);
  });

  // 4. Initialize Bootstrap Tooltips if any
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 5. Quick Application Status Form auto-submit on change
  const quickStatusSelects = document.querySelectorAll('.quick-status-select');
  quickStatusSelects.forEach(function (select) {
    select.addEventListener('change', function () {
      if (this.form) {
        this.form.submit();
      }
    });
  });
});
