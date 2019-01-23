/oauth/save - save an url to redirect to after oauth
/oauth/ - handles oauth

/api
/guilds/ - get all guilds you are on, requires oauth
/guilds/registered - get all registered guilds, requires oauth
/guilds/registered/:gid - get a particular registered guild, requires oauth

PUT /:gid/ - register a guild, manage guild
GET /:gid/responses - get responses on a guild, manage guild
GET /:gid/responses/:ind - get particular response
DELETE /:gid/responses/:ind - delete response
PATCH /:gid/responses/:ind - edit response
POST /:gid/responses/upload - upload csv file of responses
POST /:gid/responses - upload single responses

