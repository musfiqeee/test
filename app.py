import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

file_path = "Visiting Employees Tracker.xlsx"
df = None

def load_data():
    global df
    try:
        df = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
        combined = []
        for sheet_name, sheet_df in df.items():
            sheet_df.columns = [col.strip().lower() for col in sheet_df.columns]
            if all(col in sheet_df.columns for col in ["name", "arrival", "departure", "accommodation", "night stayed", "itinerary type"]):
                combined.append(sheet_df[["name", "arrival", "departure", "accommodation", "night stayed", "itinerary type"]])
        if not combined:
            globals()['df'] = None
            return
        df_combined = pd.concat(combined, ignore_index=True)
        df_combined["arrival"] = pd.to_datetime(df_combined["arrival"], errors="coerce")
        df_combined["departure"] = pd.to_datetime(df_combined["departure"], errors="coerce")
        df_combined.dropna(subset=["name", "arrival", "departure"], inplace=True)
        # Remove any row where any value matches any column name (case-insensitive, strip whitespace)
        header_names = ["name", "accommodation", "arrival", "departure", "night stayed", "itinerary type"]
        def is_header_row(row):
            return any(str(row[col]).strip().lower() == col for col in header_names)
        df_combined = df_combined[~df_combined.apply(lambda row: is_header_row(row), axis=1)]
        df_combined["year"] = df_combined["arrival"].dt.year
        df_combined["arrival_fmt"] = df_combined["arrival"].dt.strftime('%d-%b-%Y')
        df_combined["departure_fmt"] = df_combined["departure"].dt.strftime('%d-%b-%Y')
        # Debug: print first 10 rows after filtering
        print("\n[DEBUG] First 10 rows after filtering header-like rows:")
        print(df_combined.head(10).to_string())
        globals()['df'] = df_combined
    except Exception as e:
        globals()['df'] = None
        print(f"Error loading data: {e}")

load_data()
current_date = datetime.now().date()
current_year = datetime.now().year

app = Flask(__name__)

def apply_filters(data, start_date, end_date, itinerary_type, year):
    if year:
        if isinstance(year, list):
            year_list = [int(y) for y in year]
            data = data[data['year'].isin(year_list)]
        else:
            data = data[data['year'] == int(year)]
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        data = data[data['arrival'].dt.date >= start_date]
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        data = data[data['arrival'].dt.date <= end_date]
    if itinerary_type and itinerary_type.lower() != 'all':
        data = data[data['itinerary type'].str.lower() == itinerary_type.lower()]
    return data

def get_summary(data):
    if data is None or data.empty:
        return {
            'total_trips': 0,
            'total_nights': 0,
            'unique_travelers': 0,
            'unique_properties': 0
        }
    return {
        'total_trips': len(data),
        'total_nights': int(data['night stayed'].sum()),
        'unique_travelers': data['name'].nunique(),
        'unique_properties': data['accommodation'].nunique()
    }

@app.route('/update_data')
def update_data():
    load_data()
    return redirect(request.referrer or url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    itinerary_type = request.form.get('itinerary_type')
    year = request.form.getlist('year') or [str(current_year)]
    error_message = None
    if df is None:
        filtered_df = None
        summary = get_summary(None)
        years = []
        error_message = "No valid data found in the Excel file. Please check your file and try again."
    else:
        filtered_df = apply_filters(df, start_date, end_date, itinerary_type, year)
        summary = get_summary(filtered_df)
        years = sorted(df['year'].dropna().unique())
    return render_template('home.html', data=(filtered_df.to_dict(orient="records") if filtered_df is not None else []), summary=summary,
                           start_date=start_date, end_date=end_date, itinerary_type=itinerary_type,
                           year=year, years=years, error_message=error_message)

@app.route('/upcoming', methods=['GET', 'POST'])
def upcoming_travel():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    itinerary_type = request.form.get('itinerary_type')
    year = request.form.getlist('year') or [str(current_year)]
    upcoming = df[df["arrival"].dt.date > current_date]
    filtered_df = apply_filters(upcoming, start_date, end_date, itinerary_type, year)
    summary = get_summary(filtered_df)
    years = sorted(df['year'].dropna().unique())
    return render_template('table.html', title='Upcoming Travel', data=filtered_df.to_dict(orient="records"), summary=summary,
                           start_date=start_date, end_date=end_date, itinerary_type=itinerary_type,
                           year=year, years=years)

@app.route('/in_bd', methods=['GET', 'POST'])
def currently_in_bd():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    itinerary_type = request.form.get('itinerary_type')
    year = request.form.get('year') or str(current_year)
    in_bd = df[(df["arrival"].dt.date <= current_date) & (df["departure"].dt.date >= current_date)]
    filtered_df = apply_filters(in_bd, start_date, end_date, itinerary_type, year)
    summary = get_summary(filtered_df)
    years = sorted(df['year'].dropna().unique())
    return render_template('table.html', title='Currently in Bangladesh', data=filtered_df.to_dict(orient="records"), summary=summary,
                           start_date=start_date, end_date=end_date, itinerary_type=itinerary_type,
                           year=year, years=years)

@app.route('/last_travel')
def last_travel():
    if df is None:
        return render_template('table.html', title='Last Completed Travel', data=[], summary=get_summary(None), error_message="No valid data found.", start_date=None, end_date=None, itinerary_type=None, year=None, years=[])
    # Only consider travels completed before today
    completed = df[df['departure'].dt.date < current_date]
    # Find last completed travel for each traveler
    idx = completed.groupby('name')['departure'].idxmax()
    last_travels = completed.loc[idx].sort_values('name')
    summary = get_summary(last_travels)
    years = sorted(df['year'].dropna().unique())
    return render_template('table.html', title='Last Completed Travel', data=last_travels.to_dict(orient="records"), summary=summary,
                           start_date=None, end_date=None, itinerary_type=None, year=None, years=years)

if __name__ == '__main__':
    app.run(debug=False, port=8080)
