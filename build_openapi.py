from pathlib import Path
import yaml, re, json
ROOT=Path('/mnt/data/raildock-web')
OPEN=ROOT/'openapi'; OPEN.mkdir(exist_ok=True)

spec={
 'openapi':'3.1.0',
 'info':{
  'title':'RailDock API','version':'main-2026-09-19',
  'description':('HTTP API for the RailDock control plane. This reference is derived from the public main-branch Rails routes and controller behavior researched on 2026-09-19. '
                 'The repository does not currently ship a canonical OpenAPI document, so request/response schemas that are not explicit in controller code are intentionally permissive. Validate strict SDK models against the RailDock release you deploy.'),
  'license':{'name':'MIT','identifier':'MIT'}
 },
 'externalDocs':{'description':'RailDock project source','url':'https://github.com/mona-chen/raildock'},
 'servers':[{'url':'/api','description':'Same-origin RailDock control plane'},{'url':'http://localhost:8888/api','description':'Local/default installation'}],
 'tags':[], 'paths':{},
 'components':{'securitySchemes':{'bearerAuth':{'type':'http','scheme':'bearer','bearerFormat':'JWT','description':'JWT returned by POST /login.'}},'schemas':{}},
 'security':[{'bearerAuth':[]}],
 'x-raildock-source':{'repository':'https://github.com/mona-chen/raildock','researchedAt':'2026-09-19','status':'derived-reference'}
}

tag_desc={
'Health':'Control-plane health and bootstrap state.','Auth':'User authentication and current-user identity.','Webhooks':'Inbound deployment and integration callbacks.','Projects':'Project lifecycle and project-wide operations.','Environments':'Project environment lifecycle and synchronization.','Manifests':'Declarative desired-state documents, previews, apply jobs and drift.','Services':'Application and datastore service lifecycle.','Deployments':'Deployment history, state and cancellation.','Configuration':'Environment variables, domains, storage and service configuration.','Databases':'Database metadata and read-only data browsing.','Recovery':'Backups, schedules, destinations, snapshots, PITR and recovery drills.','Servers':'Deployment target creation, provisioning, validation, metrics and imports.','Organizations':'Organization lifecycle and shared operational resources.','Members':'Organization membership and invitation workflows.','Git Sources':'Repository integrations and source discovery.','Deploy Keys':'Automation/deployment credentials.','Templates':'Application templates and template deployment.','Activity':'Project and organization activity history.','Modules':'Installable RailDock modules/plugins.','Admin':'Administrative configuration, data safety and updates.','GitHub App':'GitHub App manifest, installation and webhook lifecycle.'}
spec['tags']=[{'name':k,'description':v} for k,v in tag_desc.items()]

schemas=spec['components']['schemas']
schemas.update({
 'Error':{'type':'object','properties':{'error':{'type':'string'}},'required':['error']},
 'Health':{'type':'object','properties':{'status':{'type':'string','example':'ok'},'time':{'type':'string','format':'date-time'}},'required':['status','time']},
 'User':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'email':{'type':'string','format':'email'},'name':{'type':['string','null']}}},
 'LoginRequest':{'type':'object','required':['email','password'],'properties':{'email':{'type':'string','format':'email'},'password':{'type':'string','format':'password'}}},
 'LoginResponse':{'type':'object','required':['token','user'],'properties':{'token':{'type':'string'},'user':{'$ref':'#/components/schemas/User'}}},
 'Project':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'name':{'type':'string'},'server_id':{'type':['integer','string','null']},'organization_id':{'type':['integer','string','null']}}},
 'Environment':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'name':{'type':'string'},'project_id':{'type':['integer','string']}}},
 'Service':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'name':{'type':'string'},'service_type':{'type':['string','null']},'subtype':{'type':['string','null']},'status':{'type':['string','null']},'builder':{'type':['string','null']},'git_repo':{'type':['string','null']},'branch':{'type':['string','null']},'docker_image':{'type':['string','null']},'port':{'type':['integer','string','null']},'locked':{'type':['boolean','null']},'auto_deploy':{'type':['boolean','null']},'root_directory':{'type':['string','null']},'start_command':{'type':['string','null']}}},
 'Server':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'name':{'type':'string'},'host':{'type':['string','null']},'status':{'type':['string','null']},'proxy':{'type':['string','null']},'public_ip':{'type':['string','null']}}},
 'Organization':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'name':{'type':'string'}}},
 'Deployment':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'status':{'type':['string','null']},'service_id':{'type':['integer','string']},'created_at':{'type':['string','null'],'format':'date-time'}}},
 'ManifestDocument':{'type':'object','properties':{'content':{'type':'string'},'format':{'type':'string'},'drift':{'type':['boolean','null']},'last_synced_at':{'type':['string','null'],'format':'date-time'},'last_applied_at':{'type':['string','null'],'format':'date-time'}},'additionalProperties':True},
 'Backup':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'status':{'type':['string','null']},'created_at':{'type':['string','null'],'format':'date-time'}}},
 'BackupSchedule':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'schedule':{'type':['string','null']},'enabled':{'type':['boolean','null']}}},
 'ActivityEvent':{'type':'object','additionalProperties':True,'properties':{'id':{'type':['integer','string']},'action':{'type':['string','null']},'created_at':{'type':['string','null'],'format':'date-time'}}},
 'GenericObject':{'type':'object','additionalProperties':True},
 'GenericList':{'type':'array','items':{'type':'object','additionalProperties':True}},
 'RunCommandRequest':{'type':'object','required':['command'],'properties':{'command':{'type':'string'}}},
 'DeleteConfirmation':{'type':'object','properties':{'confirmation':{'type':'string','description':'Typed confirmation value required by destructive paths.'}}},
})

id_param=lambda name: {'name':name,'in':'path','required':True,'schema':{'type':'string'}}
json_body=lambda schema=None, required=True, description=None: {'required':required,'description':description,'content':{'application/json':{'schema':schema or {'$ref':'#/components/schemas/GenericObject'}}}}

def make_id(method,path,summary):
 s=re.sub(r'[^a-zA-Z0-9]+','_',summary).strip('_').lower()
 tail=re.sub(r'[^a-zA-Z0-9]+','_',path).strip('_').lower().replace('_id_','_')
 return f"{method.lower()}_{s}_{tail}"[:100]

def op(method,path,tag,summary,desc='',security=True,body=None,params=None,response_schema=None,status='200',responses=None,operation_id=None):
 item=spec['paths'].setdefault(path,{})
 # infer path params
 inferred=[]
 for p in re.findall(r'\{([^}]+)\}',path): inferred.append(id_param(p))
 allparams=inferred+(params or [])
 resp=responses or {status:{'description':'Successful response'}}
 if response_schema and status in resp:
  resp[status]['content']={'application/json':{'schema':response_schema}}
 resp.setdefault('401',{'description':'Authentication required or token invalid','content':{'application/json':{'schema':{'$ref':'#/components/schemas/Error'}}}}) if security else None
 resp.setdefault('422',{'description':'Validation or operation error','content':{'application/json':{'schema':{'$ref':'#/components/schemas/Error'}}}})
 o={'tags':[tag],'summary':summary,'operationId':operation_id or make_id(method,path,summary),'responses':resp}
 if desc:o['description']=desc
 if allparams:o['parameters']=allparams
 if body:o['requestBody']=body
 if not security:o['security']=[]
 item[method.lower()]=o
 return o

# public/bootstrap/auth
op('GET','/health','Health','Check API health',security=False,response_schema={'$ref':'#/components/schemas/Health'})
op('GET','/setup','Health','Read initial setup state',security=False,response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/users','Auth','Create the initial user',security=False,body=json_body(),response_schema={'$ref':'#/components/schemas/User'},status='201')
op('POST','/login','Auth','Authenticate with email and password',security=False,body=json_body({'$ref':'#/components/schemas/LoginRequest'}),response_schema={'$ref':'#/components/schemas/LoginResponse'})
op('GET','/me','Auth','Get the current user',response_schema={'$ref':'#/components/schemas/User'})
op('POST','/webhooks/deploy','Webhooks','Trigger deployment webhook',security=False,body=json_body(required=False))
op('POST','/webhooks/deploy/{service_id}','Webhooks','Trigger service deployment webhook',security=False,body=json_body(required=False))

# plugins/modules
op('GET','/modules','Modules','List modules',response_schema={'$ref':'#/components/schemas/GenericList'})
for action,method,summary in [('install','POST','Install a module'),('enable','POST','Enable a module'),('disable','POST','Disable a module'),('uninstall','DELETE','Uninstall a module')]: op(method,f'/modules/{{module_id}}/{action}','Modules',summary,body=json_body(required=False) if method=='POST' else None)
op('GET','/modules/{module_id}/settings','Modules','Read module settings',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('PATCH','/modules/{module_id}/settings','Modules','Update module settings',body=json_body())

# projects
op('GET','/projects','Projects','List projects',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Project'}})
op('POST','/projects','Projects','Create a project',body=json_body(),response_schema={'$ref':'#/components/schemas/Project'},status='201')
op('GET','/projects/{project_id}','Projects','Get a project',response_schema={'$ref':'#/components/schemas/Project'})
op('PATCH','/projects/{project_id}','Projects','Update a project',body=json_body(),response_schema={'$ref':'#/components/schemas/Project'})
op('DELETE','/projects/{project_id}','Projects','Delete a project','Destructive project deletion can require a typed confirmation and/or safety snapshot precondition.',body=json_body({'$ref':'#/components/schemas/DeleteConfirmation'},required=False),responses={'200':{'description':'Project deleted or deletion state returned'},'428':{'description':'Safety precondition or explicit confirmation required','content':{'application/json':{'schema':{'$ref':'#/components/schemas/GenericObject'}}}}})
for sub,method,summary in [('activity','GET','Get project activity'),('shared_vars','GET','Get project shared variables'),('deploy_all','POST','Deploy all project services'),('cancel_deployments','POST','Cancel project deployments'),('restart_all','POST','Restart all project services'),('stop_all','POST','Stop all project services')]: op(method,f'/projects/{{project_id}}/{sub}','Projects',summary,body=json_body(required=False) if method=='POST' else None,response_schema={'$ref':'#/components/schemas/GenericList'} if method=='GET' else None)

# environments
op('GET','/projects/{project_id}/environments','Environments','List project environments',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Environment'}})
op('POST','/projects/{project_id}/environments','Environments','Create an environment',body=json_body(),response_schema={'$ref':'#/components/schemas/Environment'},status='201')
op('PATCH','/projects/{project_id}/environments/{environment_id}','Environments','Update an environment',body=json_body(),response_schema={'$ref':'#/components/schemas/Environment'})
op('DELETE','/projects/{project_id}/environments/{environment_id}','Environments','Delete an environment')
op('POST','/projects/{project_id}/environments/{environment_id}/duplicate','Environments','Duplicate an environment',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/Environment'})
op('GET','/projects/{project_id}/environments/{environment_id}/sync_plan','Environments','Preview environment synchronization',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/projects/{project_id}/environments/{environment_id}/sync','Environments','Synchronize an environment',body=json_body(required=False))

# repository import
op('POST','/projects/{project_id}/repository-import/preview','Projects','Preview repository import',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/projects/{project_id}/repository-import/apply','Projects','Apply repository import',body=json_body())

# manifests
op('GET','/projects/{project_id}/manifest','Manifests','Get project manifest',response_schema={'$ref':'#/components/schemas/ManifestDocument'})
op('PATCH','/projects/{project_id}/manifest','Manifests','Update and validate project manifest','Stores manifest content and previews its desired-state delta.',body=json_body({'type':'object','required':['content'],'properties':{'content':{'type':'string'},'format':{'type':'string'}}}),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/projects/{project_id}/manifest/preview','Manifests','Preview manifest changes',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/projects/{project_id}/manifest/apply','Manifests','Apply manifest desired state','May stop for explicit confirmation when the plan includes removals.',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/projects/{project_id}/manifest/status','Manifests','Get manifest apply status',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/projects/{project_id}/manifest/drift','Manifests','Get manifest drift report',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/projects/{project_id}/manifest/merge','Manifests','Merge current state into manifest',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})

# services collections and shallow members
op('GET','/projects/{project_id}/services','Services','List project services',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Service'}})
op('POST','/projects/{project_id}/services','Services','Create a service',body=json_body(),response_schema={'$ref':'#/components/schemas/Service'},status='201')
op('GET','/services/{service_id}','Services','Get a service',response_schema={'$ref':'#/components/schemas/Service'})
op('PATCH','/services/{service_id}','Services','Update a service',body=json_body(),response_schema={'$ref':'#/components/schemas/Service'})
op('DELETE','/services/{service_id}','Services','Delete a service','Service destruction is a guarded operation and may require explicit confirmation.',body=json_body({'$ref':'#/components/schemas/DeleteConfirmation'},required=False))
for action,method,summary in [
 ('deploy','POST','Deploy service'),('rollback','POST','Roll back service'),('start','POST','Start service'),('stop','POST','Stop service'),('restart','POST','Restart service'),('rebuild','POST','Rebuild service'),
 ('enter','POST','Open service terminal session'),('app_lock','POST','Lock service'),('unlock','POST','Unlock service'),('generate_domain','POST','Generate service domain'),('repair_env','POST','Repair service environment')]:
 op(method,f'/services/{{service_id}}/{action}','Services',summary,body=json_body(required=False))
op('POST','/services/{service_id}/scale','Services','Scale service processes',body=json_body())
op('GET','/services/{service_id}/logs','Services','Get service logs',params=[{'name':'lines','in':'query','required':False,'schema':{'type':'integer','minimum':1}}],response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/services/{service_id}/metrics','Services','Get current service metrics',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/services/{service_id}/metrics_history','Services','Get service metrics history',response_schema={'$ref':'#/components/schemas/GenericList'})
op('GET','/services/{service_id}/container_status','Services','Get container status',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/services/{service_id}/database_info','Databases','Get database information',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/services/{service_id}/backups','Recovery','List service backups',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Backup'}})
op('GET','/services/{service_id}/snapshots','Recovery','List service snapshots',response_schema={'$ref':'#/components/schemas/GenericList'})
op('GET','/services/{service_id}/backup_schedules','Recovery','List backup schedules',response_schema={'type':'array','items':{'$ref':'#/components/schemas/BackupSchedule'}})
op('POST','/services/{service_id}/backup_schedules','Recovery','Create backup schedule',body=json_body(),response_schema={'$ref':'#/components/schemas/BackupSchedule'},status='201')
op('POST','/services/{service_id}/backup','Recovery','Create service backup',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/Backup'})
op('POST','/services/{service_id}/restore','Recovery','Restore service',body=json_body())
op('POST','/services/{service_id}/run','Services','Run one-off command','The command field is required.',body=json_body({'$ref':'#/components/schemas/RunCommandRequest'}),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/services/{service_id}/lock_state','Services','Get service lock state',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/services/{service_id}/link','Services','Link service dependency',body=json_body())
op('DELETE','/services/{service_id}/unlink','Services','Unlink service dependency',body=json_body(required=False))
op('GET','/services/{service_id}/linked_by','Services','List services linked to this service',response_schema={'$ref':'#/components/schemas/GenericList'})
# service collection/config endpoints
op('GET','/projects/{project_id}/services/config_show','Configuration','Show project service configuration',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/projects/{project_id}/services/traefik_config','Configuration','Show generated Traefik configuration',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/projects/{project_id}/services/storage_list','Configuration','List service storage configuration',response_schema={'$ref':'#/components/schemas/GenericList'})

# deployments
op('GET','/services/{service_id}/deployments','Deployments','List service deployments',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Deployment'}})
op('GET','/services/{service_id}/deployments/{deployment_id}','Deployments','Get deployment',response_schema={'$ref':'#/components/schemas/Deployment'})
op('POST','/services/{service_id}/deployments/{deployment_id}/cancel','Deployments','Cancel deployment',body=json_body(required=False))

# env, domains, storage creates and global deletes/ops
op('POST','/services/{service_id}/env-vars','Configuration','Create service environment variable',body=json_body(),status='201')
op('PATCH','/services/{service_id}/env-vars/bulk','Configuration','Bulk update service environment variables',body=json_body())
op('DELETE','/services/{service_id}/env-vars/{env_var_id}','Configuration','Delete service environment variable')
op('POST','/services/{service_id}/domains','Configuration','Create service domain',body=json_body(),status='201')
op('DELETE','/services/{service_id}/domains/{domain_id}','Configuration','Delete service domain')
op('POST','/services/{service_id}/storages','Configuration','Create service storage mount',body=json_body(),status='201')
op('DELETE','/services/{service_id}/storages/{storage_id}','Configuration','Delete service storage mount')
op('GET','/services/{service_id}/storages/{storage_id}/browse','Configuration','Browse storage contents',response_schema={'$ref':'#/components/schemas/GenericObject'})
# db viewer
op('GET','/services/{service_id}/database/tables','Databases','List database tables',response_schema={'$ref':'#/components/schemas/GenericList'})
op('GET','/services/{service_id}/database/tables/{table}/rows','Databases','Browse database rows','Read-only data browser.',params=[{'name':'limit','in':'query','required':False,'schema':{'type':'integer','minimum':1}},{'name':'offset','in':'query','required':False,'schema':{'type':'integer','minimum':0}}],response_schema={'$ref':'#/components/schemas/GenericObject'})
# backup schedules/backups
op('PATCH','/services/{service_id}/backup_schedules/{schedule_id}','Recovery','Update backup schedule',body=json_body(),response_schema={'$ref':'#/components/schemas/BackupSchedule'})
op('DELETE','/services/{service_id}/backup_schedules/{schedule_id}','Recovery','Delete backup schedule')
op('GET','/services/{service_id}/backups/{backup_id}/download','Recovery','Download backup',response_schema=None)
op('POST','/services/{service_id}/backups/{backup_id}/restore','Recovery','Restore backup',body=json_body(required=False))
op('DELETE','/services/{service_id}/backups/{backup_id}','Recovery','Delete backup')
# recovery newer endpoints
op('GET','/services/{service_id}/recovery','Recovery','Get service recovery configuration',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/services/{service_id}/recovery/destinations','Recovery','Create service recovery destination',body=json_body(),status='201')
op('POST','/services/{service_id}/recovery/destinations/{destination_id}/verify','Recovery','Verify service recovery destination',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('DELETE','/services/{service_id}/recovery/destinations/{destination_id}','Recovery','Delete service recovery destination')
op('POST','/services/{service_id}/recovery/volume-snapshot','Recovery','Create volume snapshot',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('PUT','/services/{service_id}/recovery/pitr','Recovery','Configure point-in-time recovery',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('DELETE','/services/{service_id}/recovery/pitr','Recovery','Disable point-in-time recovery')
op('POST','/services/{service_id}/recovery/drill','Recovery','Start recovery drill',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('PATCH','/services/{service_id}/recovery/preferences','Recovery','Update recovery preferences',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})

# servers
op('GET','/servers','Servers','List servers',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Server'}})
op('POST','/servers','Servers','Create a server',body=json_body(),response_schema={'$ref':'#/components/schemas/Server'},status='201')
op('GET','/servers/{server_id}','Servers','Get a server',response_schema={'$ref':'#/components/schemas/Server'})
op('PATCH','/servers/{server_id}','Servers','Update a server',body=json_body(),response_schema={'$ref':'#/components/schemas/Server'})
op('DELETE','/servers/{server_id}','Servers','Delete a server')
op('POST','/servers/test','Servers','Test server connectivity',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/servers/{server_id}/provision','Servers','Provision server','Queues server provisioning using connection and proxy-mode settings.',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/servers/{server_id}/provision_status','Servers','Get server provisioning status',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/servers/{server_id}/validate','Servers','Validate server','Refreshes observed host/runtime state such as status, versions, OS, uptime, proxy and public IP.',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/Server'})
op('GET','/servers/{server_id}/metrics','Servers','Get host metrics',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/servers/{server_id}/networks','Servers','List server networks',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/servers/{server_id}/networks/validate','Servers','Validate server networks',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/servers/{server_id}/docker-imports','Servers','List Docker import candidates',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/servers/{server_id}/docker-imports','Servers','Import Docker workload',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/servers/{server_id}/unmanaged-datastores','Servers','List unmanaged datastores',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/servers/{server_id}/unmanaged-datastores/{datastore_id}/adopt','Servers','Adopt unmanaged datastore',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})

# orgs
op('GET','/organizations','Organizations','List organizations',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Organization'}})
op('POST','/organizations','Organizations','Create organization',body=json_body(),response_schema={'$ref':'#/components/schemas/Organization'},status='201')
op('GET','/organizations/{organization_id}','Organizations','Get organization',response_schema={'$ref':'#/components/schemas/Organization'})
op('PATCH','/organizations/{organization_id}','Organizations','Update organization',body=json_body(),response_schema={'$ref':'#/components/schemas/Organization'})
op('DELETE','/organizations/{organization_id}','Organizations','Delete organization')
op('GET','/organizations/{organization_id}/projects','Organizations','List organization projects',response_schema={'type':'array','items':{'$ref':'#/components/schemas/Project'}})
op('GET','/organizations/{organization_id}/server_bootstrap','Organizations','Get server bootstrap information',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/organizations/{organization_id}/data_safety','Recovery','Get organization data-safety configuration',response_schema={'$ref':'#/components/schemas/GenericObject'})
# git sources nested
op('GET','/organizations/{organization_id}/git-sources','Git Sources','List organization Git sources',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/organizations/{organization_id}/git-sources','Git Sources','Create organization Git source',body=json_body(),status='201')
for action in ['repos','branches','directories']:
 op('GET',f'/organizations/{{organization_id}}/git-sources/{{git_source_id}}/{action}','Git Sources',f'List Git source {action}',response_schema={'$ref':'#/components/schemas/GenericList'})
op('DELETE','/organizations/{organization_id}/git-sources/{git_source_id}','Git Sources','Delete organization Git source')
# members invites
op('GET','/organizations/{organization_id}/members','Members','List organization members',response_schema={'$ref':'#/components/schemas/GenericList'})
op('PATCH','/organizations/{organization_id}/members/{member_id}','Members','Update organization member',body=json_body())
op('DELETE','/organizations/{organization_id}/members/{member_id}','Members','Remove organization member')
op('GET','/organizations/{organization_id}/invitations','Members','List organization invitations',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/organizations/{organization_id}/invitations','Members','Create organization invitation',body=json_body(),status='201')
op('DELETE','/organizations/{organization_id}/invitations/{invitation_id}','Members','Revoke organization invitation')
op('GET','/invitations/{token}','Members','Get invitation by token',security=False,response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/invitations/{token}/accept','Members','Accept invitation',security=False,body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
# deploy keys
op('GET','/organizations/{organization_id}/deploy-keys','Deploy Keys','List deploy keys',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/organizations/{organization_id}/deploy-keys','Deploy Keys','Create deploy key',body=json_body(),status='201')
op('DELETE','/organizations/{organization_id}/deploy-keys/{deploy_key_id}','Deploy Keys','Delete deploy key')
# backup destinations org
op('GET','/organizations/{organization_id}/backup-destinations','Recovery','List organization backup destinations',response_schema={'$ref':'#/components/schemas/GenericList'})
op('POST','/organizations/{organization_id}/backup-destinations','Recovery','Create organization backup destination',body=json_body(),status='201')
op('PATCH','/organizations/{organization_id}/backup-destinations/{destination_id}','Recovery','Update organization backup destination',body=json_body())
op('DELETE','/organizations/{organization_id}/backup-destinations/{destination_id}','Recovery','Delete organization backup destination')
op('PATCH','/organizations/{organization_id}/backup-destinations/defaults','Recovery','Update backup destination defaults',body=json_body())
op('POST','/organizations/{organization_id}/backup-destinations/{destination_id}/verify','Recovery','Verify organization backup destination',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})

# top-level Git sources also present
op('GET','/git_sources','Git Sources','List accessible Git sources',response_schema={'$ref':'#/components/schemas/GenericList'})
for action in ['repos','branches','directories']:
 op('GET',f'/git_sources/{{git_source_id}}/{action}','Git Sources',f'List accessible Git source {action}',response_schema={'$ref':'#/components/schemas/GenericList'})
# top-level deploy keys
op('GET','/deploy_keys','Deploy Keys','List accessible deploy keys',response_schema={'$ref':'#/components/schemas/GenericList'})

# templates, activity, builders config
op('GET','/templates','Templates','List templates',response_schema={'$ref':'#/components/schemas/GenericList'})
op('GET','/templates/{template_id}','Templates','Get template',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/templates/{template_id}/deploy','Templates','Deploy template',body=json_body(),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/activity','Activity','List global activity',response_schema={'type':'array','items':{'$ref':'#/components/schemas/ActivityEvent'}})
op('GET','/builders','Configuration','List available builders',response_schema={'$ref':'#/components/schemas/GenericList'})
op('GET','/config','Configuration','Get client configuration',response_schema={'$ref':'#/components/schemas/GenericObject'})

# admin
op('GET','/admin/settings','Admin','Get admin settings',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('PATCH','/admin/settings','Admin','Update admin settings',body=json_body())
op('POST','/admin/settings/test-github-app','Admin','Test GitHub App settings',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/admin/settings/test-smtp','Admin','Test SMTP settings',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/admin/data-safety','Admin','Get system data-safety state',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/admin/update','Admin','Get update state',response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/admin/update/check','Admin','Check for RailDock updates',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('POST','/admin/update/apply','Admin','Apply RailDock update',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('PATCH','/admin/update/auto-update','Admin','Update automatic-update preference',body=json_body())

# github app public/auth mix
op('POST','/github_app/manifest','GitHub App','Create GitHub App manifest flow',body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/github_app/callback','GitHub App','Handle GitHub App callback',security=False,params=[{'name':'code','in':'query','required':False,'schema':{'type':'string'}}],response_schema={'$ref':'#/components/schemas/GenericObject'})
op('GET','/github_app/setup','GitHub App','Handle GitHub App setup callback',security=False,params=[{'name':'code','in':'query','required':False,'schema':{'type':'string'}}],response_schema={'$ref':'#/components/schemas/GenericObject'})
op('DELETE','/github_app/installation','GitHub App','Remove GitHub App installation')
op('POST','/github_app/webhook','GitHub App','Receive GitHub App webhook',security=False,body=json_body(required=False),response_schema={'$ref':'#/components/schemas/GenericObject'})

# global errors / ensure no operation ID collisions
seen={}
for path,item in spec['paths'].items():
 for method,o in item.items():
  oid=o['operationId']; seen[oid]=seen.get(oid,0)+1
for path,item in spec['paths'].items():
 for method,o in item.items():
  if seen[o['operationId']]>1: o['operationId'] += '_' + str(abs(hash(path+method))%100000)

out=OPEN/'raildock.openapi.yaml'
out.write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True,width=110))
print('paths',len(spec['paths']),'operations',sum(len(v) for v in spec['paths'].values()),'->',out)
