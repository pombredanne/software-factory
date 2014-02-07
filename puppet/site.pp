node base {
  # these are imported from modules/base
  include disable_root_pw_login
  include ssh_keys
  include hosts
}

node default inherits base {
}

node /.*redmine.*/ inherits base {
  include redmine
}