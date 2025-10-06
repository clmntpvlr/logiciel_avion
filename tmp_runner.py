from pathlib import Path
import sys
sys.path.append('.')
from aircraft_designer.modules.database.repository import DatabaseRepository

p = Path('tmp_test_db.sqlite')
try:
    repo = DatabaseRepository(p)
    jane = Path('aircraft_designer/modules/database/json_avions_janes_2011-2012/AAK_Hornet.json')
    repo.import_json(jane)
    aircrafts = repo.list_aircrafts()
    print('aircrafts:', [a.name for a in aircrafts])
    chars = repo.list_characteristics()
    print('chars sample:', [c.name for c in chars][:8])
    if aircrafts:
        vals = repo.get_values_for_aircraft(aircrafts[0].id)
        print('values count:', len(vals))
        for v in vals[:10]:
            print(v)
finally:
    try:
        Path('tmp_test_db.sqlite').unlink()
    except Exception:
        pass
