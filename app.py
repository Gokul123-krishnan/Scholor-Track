"""
Scholar Track - Scholarship Management System
Flask Web Application Entrypoint and Routing Module
"""

import os
from datetime import datetime, date
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
import database

app = Flask(__name__)
# Secret key for session management and flash alerts
app.secret_key = os.environ.get('SECRET_KEY', 'scholar-track-secret-key-2026-secure-development')

# Ensure database and table exist upon startup
with app.app_context():
    database.init_db()


@app.context_processor
def inject_global_template_vars():
    """Inject globally available variables into all Jinja2 templates."""
    return {
        'current_year': datetime.now().year,
        'today_date': date.today().strftime('%Y-%m-%d'),
        'today_display': date.today().strftime('%A, %b %d, %Y'),
        'valid_statuses': database.VALID_STATUSES
    }


# ==========================================
# 1. DASHBOARD ROUTE
# ==========================================
@app.route('/')
def index():
    """Render the main analytics dashboard with stats and upcoming deadlines."""
    try:
        stats = database.get_dashboard_statistics()
        return render_template('index.html', stats=stats, active_page='dashboard')
    except Exception as e:
        app.logger.error(f"Error loading dashboard: {e}")
        flash(f"Error loading dashboard statistics: {str(e)}", "danger")
        return render_template('index.html', stats=None, active_page='dashboard')


# ==========================================
# 2. SCHOLARSHIP LIST, SEARCH & FILTER
# ==========================================
@app.route('/scholarships')
def scholarships():
    """
    Display all scholarships with real-time search, status filtering,
    deadline filtering, and custom sorting.
    """
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'All').strip()
    deadline_filter = request.args.get('deadline_status', 'all').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    try:
        scholarship_list = database.get_all_scholarships(
            search_query=search_query,
            status_filter=status_filter,
            deadline_filter=deadline_filter,
            sort_by=sort_by
        )
    except Exception as e:
        app.logger.error(f"Error fetching scholarships: {e}")
        flash(f"Could not retrieve scholarships: {str(e)}", "danger")
        scholarship_list = []

    return render_template(
        'scholarships.html',
        scholarships=scholarship_list,
        total_count=len(scholarship_list),
        search_query=search_query,
        current_status=status_filter,
        current_deadline_status=deadline_filter,
        current_sort=sort_by,
        active_page='scholarships'
    )


# ==========================================
# 3. SCHOLARSHIP DETAILS
# ==========================================
@app.route('/scholarships/<int:scholarship_id>')
def scholarship_details(scholarship_id):
    """View complete details of a single scholarship."""
    scholarship = database.get_scholarship_by_id(scholarship_id)
    if not scholarship:
        flash("Scholarship record not found.", "warning")
        abort(404)

    return render_template(
        'scholarship_details.html',
        scholarship=scholarship,
        active_page='scholarships'
    )


# ==========================================
# 4. ADD SCHOLARSHIP
# ==========================================
@app.route('/scholarships/new', methods=['GET', 'POST'])
def add_scholarship():
    """Handle adding a new scholarship with form validation."""
    if request.method == 'POST':
        name = request.form.get('scholarship_name', '').strip()
        provider = request.form.get('provider', '').strip()
        description = request.form.get('description', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        deadline = request.form.get('deadline', '').strip()
        application_link = request.form.get('application_link', '').strip()
        application_status = request.form.get('application_status', 'Pending').strip()

        # Validation
        errors = []
        if not name:
            errors.append("Scholarship name is required.")
        if not provider:
            errors.append("Provider / Organization name is required.")
        if not deadline:
            errors.append("Application deadline is required.")
        else:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid deadline date format. Please use YYYY-MM-DD.")

        # Amount validation
        amount = 0.0
        if amount_raw:
            try:
                amount = float(amount_raw)
                if amount < 0:
                    errors.append("Scholarship amount cannot be negative.")
            except ValueError:
                errors.append("Please enter a valid numeric value for the scholarship amount.")

        # Application link validation
        if application_link and not (application_link.startswith('http://') or application_link.startswith('https://')):
            application_link = 'https://' + application_link

        if application_status not in database.VALID_STATUSES:
            application_status = 'Pending'

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'add_scholarship.html',
                form_data=request.form,
                active_page='add_scholarship'
            )

        try:
            new_id = database.add_scholarship(
                name=name,
                provider=provider,
                description=description,
                eligibility=eligibility,
                amount=amount,
                deadline=deadline,
                application_link=application_link,
                application_status=application_status
            )
            flash(f"Scholarship '{name}' was successfully added!", "success")
            return redirect(url_for('scholarship_details', scholarship_id=new_id))
        except Exception as e:
            app.logger.error(f"Error inserting scholarship: {e}")
            flash(f"Database error while saving scholarship: {str(e)}", "danger")
            return render_template('add_scholarship.html', form_data=request.form, active_page='add_scholarship')

    return render_template('add_scholarship.html', form_data={}, active_page='add_scholarship')


# ==========================================
# 5. EDIT SCHOLARSHIP
# ==========================================
@app.route('/scholarships/<int:scholarship_id>/edit', methods=['GET', 'POST'])
def edit_scholarship(scholarship_id):
    """Handle editing an existing scholarship record."""
    scholarship = database.get_scholarship_by_id(scholarship_id)
    if not scholarship:
        flash("Scholarship not found.", "warning")
        abort(404)

    if request.method == 'POST':
        name = request.form.get('scholarship_name', '').strip()
        provider = request.form.get('provider', '').strip()
        description = request.form.get('description', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        deadline = request.form.get('deadline', '').strip()
        application_link = request.form.get('application_link', '').strip()
        application_status = request.form.get('application_status', 'Pending').strip()

        # Validation
        errors = []
        if not name:
            errors.append("Scholarship name is required.")
        if not provider:
            errors.append("Provider is required.")
        if not deadline:
            errors.append("Deadline is required.")
        else:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid deadline format. Use YYYY-MM-DD.")

        amount = 0.0
        if amount_raw:
            try:
                amount = float(amount_raw)
                if amount < 0:
                    errors.append("Amount cannot be negative.")
            except ValueError:
                errors.append("Amount must be a valid number.")

        if application_link and not (application_link.startswith('http://') or application_link.startswith('https://')):
            application_link = 'https://' + application_link

        if application_status not in database.VALID_STATUSES:
            application_status = 'Pending'

        if errors:
            for error in errors:
                flash(error, 'danger')
            # Retain user input in form
            updated_data = dict(scholarship)
            updated_data.update(request.form)
            return render_template('edit_scholarship.html', scholarship=updated_data, active_page='scholarships')

        try:
            success = database.update_scholarship(
                scholarship_id=scholarship_id,
                name=name,
                provider=provider,
                description=description,
                eligibility=eligibility,
                amount=amount,
                deadline=deadline,
                application_link=application_link,
                application_status=application_status
            )
            if success:
                flash(f"Scholarship '{name}' updated successfully!", "success")
            else:
                flash("No changes were made or record was not found.", "info")
            return redirect(url_for('scholarship_details', scholarship_id=scholarship_id))
        except Exception as e:
            app.logger.error(f"Error updating scholarship: {e}")
            flash(f"Database error while updating: {str(e)}", "danger")

    return render_template('edit_scholarship.html', scholarship=scholarship, active_page='scholarships')


# ==========================================
# 6. DELETE SCHOLARSHIP
# ==========================================
@app.route('/scholarships/<int:scholarship_id>/delete', methods=['POST'])
def delete_scholarship(scholarship_id):
    """Delete a scholarship record and redirect with confirmation."""
    scholarship = database.get_scholarship_by_id(scholarship_id)
    if not scholarship:
        flash("Scholarship not found.", "warning")
        return redirect(url_for('scholarships'))

    name = scholarship['scholarship_name']
    try:
        deleted = database.delete_scholarship(scholarship_id)
        if deleted:
            flash(f"Scholarship '{name}' has been permanently deleted.", "success")
        else:
            flash("Unable to delete scholarship. Please try again.", "danger")
    except Exception as e:
        app.logger.error(f"Error deleting scholarship {scholarship_id}: {e}")
        flash(f"Database error deleting record: {str(e)}", "danger")

    return redirect(url_for('scholarships'))


# ==========================================
# 7. QUICK STATUS UPDATE (AJAX or Form)
# ==========================================
@app.route('/scholarships/<int:scholarship_id>/status', methods=['POST'])
def update_status(scholarship_id):
    """Update application status quickly from cards, table, or details view."""
    # Check if request has JSON or Form data
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form.get('status')

    if new_status not in database.VALID_STATUSES:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        flash("Invalid application status specified.", "danger")
        return redirect(request.referrer or url_for('scholarships'))

    success = database.update_scholarship_status(scholarship_id, new_status)

    if request.is_json:
        return jsonify({
            'success': success,
            'status': new_status,
            'message': f"Status updated to {new_status}"
        })

    if success:
        flash(f"Application status updated to '{new_status}'.", "success")
    else:
        flash("Failed to update application status.", "danger")

    return redirect(request.referrer or url_for('scholarship_details', scholarship_id=scholarship_id))


# ==========================================
# 8. ERROR HANDLERS
# ==========================================
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Custom 500 handler."""
    return render_template('500.html'), 500


# ==========================================
# APP LAUNCHER
# ==========================================
if __name__ == '__main__':
    # Run development server on http://127.0.0.1:5000/
    print("=" * 60)
    print(" Scholar Track - Scholarship Management System")
    print(" Server running locally at: http://127.0.0.1:5000/")
    print(" Press CTRL+C to stop the server.")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
