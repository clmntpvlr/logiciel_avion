from aircraft_designer.core.project_manager import create_project, list_projects
print('before', list_projects())
proj = create_project('TestDiag')
print('created path', proj.path)
print('after', list_projects())
