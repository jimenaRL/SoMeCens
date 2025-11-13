# 4.3 export excel for debugging
excelfile = os.path.join(exportsfolder, f'localized_users_{country.replace(' ', '')}.xlsx')
with pd.ExcelWriter(excelfile) as writer:

    # export matchs per unit
    data = []
    statsHeaders = [
        'level',
        'code',
        'label',
        'unit population',
        'matched users',
        'total matched users (with descendant)',
        'total matched users percent (with descendant)',
        'subunits'
    ]

    for g in demo.geoUnits:
        stats = demo.getGeoUnitLocalizationsStats(g.code)
        subunits = demo.getSubUnits(g.code)
        stats.append(' | '.join(subunits))
        data.append(stats)

    predata = [["NUTS level", "mean matched %", "median matched %", "mean pop.", "median pop.", "", "", ""]]
    for l in range(demo.getDeepestLevel() + 1):
        mean_perc = np.mean([d[6] for d in data if d[0]==l])
        median_perc = np.median([d[6] for d in data if d[0]==l])
        mean_pop = np.mean([d[3] for d in data if d[0]==l])
        median_pop = np.median([d[3] for d in data if d[0]==l])
        predata.append([str(l), f"{mean_perc:.2f}", f"{median_perc:.2f}", f"{mean_pop:.0f}", f"{median_pop:.0f}", "", "", ""])
    predata.append(["", "", "", "", "", "", "", ""])
    predata.append(["", "", "", "", "", "", "", ""])

    predata.append(statsHeaders)

    df = pd.DataFrame(data=predata+data)
    df.to_excel(writer, index=False, sheet_name=f"statistics")

    # export users matchs
    columns = ["pseudo_id", "location", "screen_name", "normalized_location"]
    for g in demo.geoUnits:
        users = demo.getLocalizedUsers(code=g.code, descendants=False)[g.code]
        stats = demo.getGeoUnitLocalizationsStats(g.code)

        predata = [
            ["Level", g.level, "", ""],
            ["Code", g.code, "", ""],
            ["Label", g.label, "", ""],
            ["Population", stats[3], "", ""],
            ["Matchs", stats[4], "", ""],
            ["Subunits", ' | '.join(demo.getSubUnits(g.code)), "", ""],
            ["", "", "", ""],
        ]
        predata.append(columns)
        df = pd.DataFrame(data=predata+users)
        df = df.drop(df.columns[2], axis=1)
        df = df.iloc[:nbuserdump]
        df = df.map(
                lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        df.to_excel(writer, index=False, sheet_name=f"{g.code}")

print(f"Mathch file save at {excelfile}")
# os.system(f"open {excelfile}")
