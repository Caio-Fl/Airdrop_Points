def protocol_rate(tvl,top100,roi,daily_points_rate,users,hype):

    tvl = tvl*1000000

    # TVL grade
    if tvl <= 1000000:
        tvl_grade = 0
    elif 1000000 < tvl <= 10000000:
        tvl_grade = 1
    elif 10000000 < tvl <= 50000000:
        tvl_grade = 2
    elif 50000000 < tvl <= 100000000:
        tvl_grade = 3
    elif 100000000 < tvl <= 150000000:
        tvl_grade = 4
    elif 150000000 < tvl <= 250000000:
        tvl_grade = 5
    elif 250000000 < tvl <= 500000000:
        tvl_grade = 6
    else:
        tvl_grade = 7
    
    # Top 100 grade
    if top100 >= 80:
        top100_grade = 0
    elif 70 <= top100 < 80:
        top100_grade = 1
    elif 60 <= top100 < 70:
        top100_grade = 2
    elif 50 < top100 < 60:
        top100_grade = 3
    elif 30 < top100 < 50:
        top100_grade = 4
    elif 30 < top100 < 40:
        top100_grade = 5
    elif 20 < top100 < 30:
        top100_grade = 6
    else:
        top100_grade = 7

    # ROI
    if roi <= 40:
        roi_grade = 0
    elif 40 < roi <= 60:
        roi_grade = 1
    elif 60 < roi <= 80:
        roi_grade = 2
    elif 80 < roi <= 100:
        roi_grade = 3
    elif 100 < roi <= 125:
        roi_grade = 4
    elif 125< roi <= 150:
        roi_grade = 5
    elif 150 < roi <= 250:
        roi_grade = 6
    else:
        roi_grade = 7

    # Raising Daily Points Rate
    if daily_points_rate >= 5.5 or daily_points_rate <= 0.4:
        dpr_grade = 0
    elif 5 <= daily_points_rate < 5.5:
        dpr_grade = 1 
    elif 4.5 <= daily_points_rate < 5:
        dpr_grade = 2 
    elif 3.5 <= daily_points_rate < 4.5:
        dpr_grade = 3
    elif 2.5 <= daily_points_rate < 3.5:
        dpr_grade = 4 
    elif 1.5 <= daily_points_rate < 2.5:
        dpr_grade = 5 
    elif 1 <= daily_points_rate < 1.5:
        dpr_grade = 6 
    elif 0.4 <= daily_points_rate < 1:
        dpr_grade = 7 

    # Users
    if users <= 500 or users >= 120000:
        users_grade = 0
    elif 500 < users <= 2000 or 100000 < users <= 120000:
        users_grade  = 1
    elif 2000 < users <= 5000 or 80000 < users <= 100000:
        users_grade  = 2
    elif 5000 < users <= 7500 or 50000 < users <= 80000:
        users_grade  = 3
    elif 7500 < users <= 10000 or 30000 < users <= 50000:
        users_grade  = 4
    elif 10000 < users <= 15000:
        users_grade  = 5
    elif 15000 < users <= 20000:
        users_grade = 6
    else:
        users_grade = 7
    
    # Hype
    if hype == "pessimo" or hype == "":
        hype_grade = 0
    elif hype == "ruim":
        hype_grade = 1
    elif hype == "fraco":
        hype_grade = 2
    elif hype == "bom":
        hype_grade = 3
    elif hype == "muito bom":
        hype_grade = 4
    elif hype == "otimo":
        hype_grade = 5
    elif hype == "excelente":
        hype_grade = 6
    elif hype == "top":
        hype_grade = 7

    grade = round(10*((1.5*tvl_grade)+(top100_grade)+(1.5*roi_grade)+(dpr_grade)+(users_grade)+(hype_grade))/(2*7*6),2)
    print((1.5*tvl_grade),top100_grade,(1.5*roi_grade),dpr_grade,users_grade,hype_grade)
    if grade < 0.5:
        stars = "☆☆☆☆☆ - " + str(grade)
    elif 0.5 <= grade < 1.5:
        stars = "⭐☆☆☆☆ - " + str(grade)
    elif 1.5 <= grade < 2.5:
        stars = "⭐⭐☆☆☆ - " + str(grade)
    elif 2.5 <= grade < 3.5:
        stars = "⭐⭐⭐☆☆ - " + str(grade)
    elif 3.5 <= grade < 4.5:
        stars = "⭐⭐⭐⭐☆ - " + str(grade)
    else:
        stars = "⭐⭐⭐⭐⭐ - " + str(grade)

    return(stars)