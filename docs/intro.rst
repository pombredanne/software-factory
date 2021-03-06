Contents:

.. toctree::

Introduction to Software Factory
================================

Software Factory is a collection of existing tools that aim to
provide a powerful platform to collaborate on software development.
Software Factory eases the deployment of this platform and adds an
additional management layer. The deployment target is an
OpenStack compatible cloud.

What is Software Factory
------------------------

The platform deployed by Software Factory is based on two main
tools that you may already know: Gerrit and Jenkins. This couple
has proven its robustness in some huge projects and especially
OpenStack were hundreds of commit are pushed and automatically
tested every day.

Software Factory will highly facilitate the deployment and
configuration of such tools. Instead of losing time to
try to understand deployment details of each component,
Software Factory will bootstrap a working platform
within a couple of minutes.

An OpenStack or OpenStack compatible cloud account is needed
to deploy the Software Factory stack. The bootstrap process
will boot all the VMs needed by the platform. Basically
the bootstrap process will take care of all deployment details
from uploading Software Factory's pre-built images to
inter-connection configuration of Gerrit and Jenkins for
instance. At the end of this process your new development
platform is ready to use.

Later in this guide we will use SF as Software Factory.

Which components SF provides
----------------------------

The stack is composed of three main components:

* A code review component : `Gerrit <http://en.wikipedia.org/wiki/Gerrit_%28software%29>`_
* A continuous integration system : `Jenkins <http://en.wikipedia.org/wiki/Jenkins_%28software%29>`_
* A Smart project gating system: `Zuul <http://ci.openstack.org/zuul/>`_
* A project management and bug tracking system : `Redmine <http://en.wikipedia.org/wiki/Redmine>`_
* A collaborative real time editor : `Etherpad <http://en.wikipedia.org/wiki/Etherpad>`_
* A `pastebin <http://en.wikipedia.org/wiki/Pastebin>`_ like tool : Lodgeit

Which features SF provides
--------------------------

Ready to use development platform
.................................

Setting up a development environment manually can really be
time consuming and sometimes leads to a lot of configuration
trouble. SF provides a way to easily deploy such environment
on a running OpenStack cloud. The deployment mainly uses OpenStack
Heat to deploy cloud resources like virtual machines, block
volumes, network security groups, and floating IPs. Internal
configuration of services like Gerrit, Jenkins, and others is done
by Puppet. At the end of the process the SF environment deployment
is ready to be used. The whole process from image uploading
to the system up and ready can take a couple minutes.

Below is an overview of all nodes (shown as dashed boxes) and services
and their connections to each other. Not shown is the puppetmaster server.
Each node runs a puppet agent that connects to the puppetmaster server.

.. graphviz:: components.dot

Gerrit
......

Gerrit is the main component of SF. It provides the Git
server, a code review mechanism, and a powerful ACL system. SF
properly configures Gerrit to integrate correctly with
the issues tracker (Redmine) and the CI system (Jenkins/Zuul).

Some useful plugins are installed on Gerrit:

* Reviewer-by-blame: Automatically adds code reviewers to submitted changes according
  to git-blame result.
* Replication: Add replication mechanism to synchronize internal Git repositories
  to remote location.
* Gravatar: Because sometimes it is quite fun to have its gravatar along its
  commits and messages.
* Delete-project: Let the admin the ability to fully remove an useless Gerrit project.
* Download-commands: Ease integration of Gerrit with IDE

Some Gerrit hooks are installed to handle Redmine issues:

* An issue referenced in a commit message will be automatically
  set as "In progress" in Redmine.
* An issue referenced by a change will be closed when Gerrit merges it.

Gerrit is configured to work with Zuul and Jenkins, that means
project tests can be run when changes are proposed to a project.
Tests results are published on Gerrit as a note and can
prevent a change to be merged on the master branch.

.. image:: imgs/gerrit.jpg

Jenkins/Zuul
............

Jenkins is deployed along with SF as the CI component. It is
configured to work with Zuul. Zuul will control how Jenkins
perform jobs. The SF deployment configures a first Jenkins VM
as master and one Jenkins VM as slave. Additional other Jenkins slaves
can be easily added afterwards.

.. image:: imgs/jenkins.jpg

On SF Zuul is by default configured to provide four pipelines:

* A check pipeline
* A gate pipeline
* A post pipeline
* A periodic pipeline

.. image:: imgs/zuul.jpg

Redmine
.......

Redmine is the issue tracker inside Software Factory. Redmine
configuration done by in SF is quite standard. Additionally
we embed the "Redmine Backlogs" plugin that eases Agile
methodologies to be used with Redmine.

.. image:: imgs/redmine.jpg

Etherpad and Lodgeit
....................

The Software Factory deploys along with Redmine, Gerrit and Jenkins two
additional collaboration tools. The first one is an Etherpad where team members can
live edit text documents to collaborate. This is really handy for instance to
brainstorm of design documents.

.. image:: imgs/etherpad.jpg

The second, Lodgeit, is a pastebin like tool that facilitates rapid
sharing of code snippets, error stack traces, ...

.. image:: imgs/paste.jpg

Unified project creation
........................

SF provides a REST service that can be used to ease SF management.
Thanks to it you can easily for instance :

* Create a project and its related user groups in a unified way.
* Add/remove users from project groups in a unified way.
* Delete a project with its related group in a unified way.
* Perform and restore a backup of the SF user data.

By unified way we mean action is performed in Gerrit and on Redmine, for
instance if a user is added to the admin group of a project A
it is also added on the related Redmine and Gerrit group automatically.

Top menu - One entry point
..........................

In order to ease the usage of all those nice tools, SF provides
an unique portal served by only one remotely accessible HTTP server.
That means only one hostname to remember in order to access all
the services. Each web interface will be displayed with
a little menu on the top of your Web browser screen. 
You can move around all SF services with one click.

Single Sign On
..............

As it is always a pain to deal with login/logout of each component, the
SF provides an unified authentication through Gerrit, Redmine and Jenkins.
Once your are authenticated on Gerrit your are also logged in on Redmine and Jenkins.
A logout from one service logs you out from other services as well.

Currently SF provides two kind of backends to authenticate:

* LDAP backend
* Github OAuth

.. image:: imgs/login.jpg

Below is the sequence diagram of the SSO mechanism.

.. graphviz:: authentication.dot

The future of Software Factory
------------------------------

We want to provide :

* More ready to use integration between components.
* Ready and easy to use updates for SF deployments.
* Autoscaling using Heat.
* Developer, Project leaders, Scrum master useful dashboard.
* Provide choice over issues tracker at deployment time.
