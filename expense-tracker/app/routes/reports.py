from flask import Blueprint, render_template, request, session, redirect, url_for, flash, make_response
from app.models import Expense, Income, Budget, User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from io import BytesIO

# Try to import ReportLab, but provide fallback if not available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. PDF generation will be disabled.")

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET', 'POST'])
def reports():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            report_type = request.form.get('report_type')
            period = request.form.get('period')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not REPORTLAB_AVAILABLE:
                flash('PDF generation is not available. Please install ReportLab library.', 'error')
                return redirect(url_for('reports.reports'))
            
            # Generate and return PDF
            pdf_response = generate_pdf_report(
                user_id=session['user_id'],
                report_type=report_type,
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            
            if pdf_response:
                return pdf_response
            else:
                flash('Error generating report. Please try again.', 'error')
                
        except Exception as e:
            print(f"Report generation error: {e}")
            flash('Error generating report. Please try again.', 'error')
        
        return redirect(url_for('reports.reports'))
    
    # Get chart data for visualization
    chart_data = get_chart_data(session['user_id'])
    
    return render_template('reports.html', 
                         reportlab_available=REPORTLAB_AVAILABLE,
                         chart_data=chart_data)

def get_chart_data(user_id):
    """Get aggregated data for charts"""
    try:
        # Get last 6 months of data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)  # ~6 months
        
        # Get monthly expense data
        expense_data = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).group_by(func.strftime('%Y-%m', Expense.date)).all()
        
        # Get monthly income data
        income_data = db.session.query(
            func.strftime('%Y-%m', Income.date).label('month'),
            func.sum(Income.amount).label('total')
        ).filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date <= end_date
        ).group_by(func.strftime('%Y-%m', Income.date)).all()
        
        # Get expense by category for pie chart
        category_data = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).group_by(Expense.category).all()
        
        # Generate last 6 months labels
        months = []
        current_date = datetime.now().date()
        for i in range(5, -1, -1):  # Last 6 months
            month_date = current_date.replace(day=1) - timedelta(days=i*30)
            months.append(month_date.strftime('%Y-%m'))
        
        # Create data dictionaries
        expense_dict = {item.month: float(item.total) for item in expense_data}
        income_dict = {item.month: float(item.total) for item in income_data}
        
        # Fill missing months with 0
        expense_amounts = [expense_dict.get(month, 0) for month in months]
        income_amounts = [income_dict.get(month, 0) for month in months]
        
        # Format month names for display
        month_labels = []
        for month in months:
            try:
                date_obj = datetime.strptime(month, '%Y-%m')
                month_labels.append(date_obj.strftime('%b %Y'))
            except:
                month_labels.append(month)
        
        return {
            'months': month_labels,
            'expenses': expense_amounts,
            'income': income_amounts,
            'categories': [item.category for item in category_data],
            'category_amounts': [float(item.total) for item in category_data]
        }
        
    except Exception as e:
        print(f"Chart data error: {e}")
        return {
            'months': [],
            'expenses': [],
            'income': [],
            'categories': [],
            'category_amounts': []
        }

def get_date_range(period, start_date=None, end_date=None):
    """Get start and end dates based on period selection"""
    today = datetime.now().date()
    
    if period == 'current_month':
        start = today.replace(day=1)
        end = today
    elif period == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        start = last_month.replace(day=1)
        end = last_month
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        end = today
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today
    elif period == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start = today.replace(day=1)
        end = today
    
    return start, end

def generate_pdf_report(user_id, report_type, period, start_date=None, end_date=None):
    """Generate PDF report based on parameters"""
    if not REPORTLAB_AVAILABLE:
        return None
        
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        start, end = get_date_range(period, start_date, end_date)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        
        report_title = f"{report_type.title()} Report"
        story.append(Paragraph(report_title, title_style))
        
        info_style = styles['Normal']
        story.append(Paragraph(f"<b>User:</b> {user.name}", info_style))
        story.append(Paragraph(f"<b>Email:</b> {user.email}", info_style))
        story.append(Paragraph(f"<b>Period:</b> {start} to {end}", info_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        story.append(Spacer(1, 20))
        
        if report_type == 'expenses':
            generate_expenses_report(story, user_id, start, end, styles)
        elif report_type == 'income':
            generate_income_report(story, user_id, start, end, styles)
        elif report_type == 'budget':
            generate_budget_report(story, user_id, start, end, styles)
        elif report_type == 'summary':
            generate_summary_report(story, user_id, start, end, styles)
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None

def generate_expenses_report(story, user_id, start_date, end_date, styles):
    """Generate expenses section of report"""
    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).order_by(Expense.date.desc()).all()
    
    story.append(Paragraph("<b>Expense Details</b>", styles['Heading2']))
    
    if expenses:
        data = [['Date', 'Category', 'Description', 'Amount']]
        total_amount = 0
        
        for expense in expenses:
            data.append([
                expense.date.strftime('%Y-%m-%d'),
                expense.category,
                expense.description or 'No description',
                f'${expense.amount:.2f}'
            ])
            total_amount += expense.amount
        
        data.append(['', '', 'TOTAL:', f'${total_amount:.2f}'])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Summary:</b> {len(expenses)} expenses totaling ${total_amount:.2f}", styles['Normal']))
    else:
        story.append(Paragraph("No expenses found for the selected period.", styles['Normal']))

def generate_income_report(story, user_id, start_date, end_date, styles):
    """Generate income section of report"""
    incomes = Income.query.filter(
        Income.user_id == user_id,
        Income.date >= start_date,
        Income.date <= end_date
    ).order_by(Income.date.desc()).all()
    
    story.append(Paragraph("<b>Income Details</b>", styles['Heading2']))
    
    if incomes:
        data = [['Date', 'Source', 'Description', 'Amount']]
        total_amount = 0
        
        for income in incomes:
            data.append([
                income.date.strftime('%Y-%m-%d'),
                income.source,
                income.description or 'No description',
                f'${income.amount:.2f}'
            ])
            total_amount += income.amount
        
        data.append(['', '', 'TOTAL:', f'${total_amount:.2f}'])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Summary:</b> {len(incomes)} income entries totaling ${total_amount:.2f}", styles['Normal']))
    else:
        story.append(Paragraph("No income found for the selected period.", styles['Normal']))

def generate_budget_report(story, user_id, start_date, end_date, styles):
    """Generate budget section of report"""
    budgets = Budget.query.filter_by(user_id=user_id).all()
    
    story.append(Paragraph("<b>Budget Analysis</b>", styles['Heading2']))
    
    if budgets:
        data = [['Category', 'Budget', 'Spent', 'Remaining', 'Status']]
        
        for budget in budgets:
            spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                Expense.category == budget.category,
                Expense.date >= start_date,
                Expense.date <= end_date
            ).scalar() or 0
            
            remaining = budget.amount - spent
            status = "On Track" if remaining >= 0 else "Over Budget"
            
            data.append([
                budget.category,
                f'${budget.amount:.2f}',
                f'${spent:.2f}',
                f'${remaining:.2f}',
                status
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No budgets set.", styles['Normal']))

def generate_summary_report(story, user_id, start_date, end_date, styles):
    """Generate complete financial summary"""
    story.append(Paragraph("<b>Financial Summary</b>", styles['Heading2']))
    
    total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar() or 0
    
    total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(
        Income.user_id == user_id,
        Income.date >= start_date,
        Income.date <= end_date
    ).scalar() or 0
    
    net_savings = total_income - total_expenses
    
    data = [
        ['Metric', 'Amount'],
        ['Total Income', f'${total_income:.2f}'],
        ['Total Expenses', f'${total_expenses:.2f}'],
        ['Net Savings', f'${net_savings:.2f}']
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    generate_expenses_report(story, user_id, start_date, end_date, styles)
    story.append(Spacer(1, 20))
    generate_income_report(story, user_id, start_date, end_date, styles)
