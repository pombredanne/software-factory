#!/bin/bash

set -x

source ../functions.sh
. ./../../role_configrc
. conf

generate_sfconfig
if [ -n "$FROMUPSTREAM" ]; then
    BUILT_ROLES=$UPSTREAM
else
    BUILT_ROLES=$INST
fi
STACKNAME=${STACKNAME:-SoftwareFactory}
DOMAIN=$(cat $SFCONFIGFILE | grep "^domain:" | cut -d' ' -f2)
suffix=$DOMAIN

[ -n "${NOVA_KEYNAME}" ] && key_name="${NOVA_KEYNAME}" || {
    [ -n "${HEAT_TENANT}" ] && key_name="${HEAT_TENANT}"
}

jenkins_user_pwd=$(generate_random_pswd 8)
jenkins_master_url="jenkins.$suffix"

params="key_name=$key_name;suffix=$suffix"

params="$params;puppetmaster_flavor=$puppetmaster_flavor"
params="$params;mysql_flavor=$mysql_flavor"
params="$params;managesf_flavor=$managesf_flavor"
params="$params;gerrit_flavor=$gerrit_flavor"
params="$params;redmine_flavor=$redmine_flavor"
params="$params;jenkins_flavor=$jenkins_flavor"
params="$params;slave_flavor=$slave_flavor"

params="$params;puppetmaster_root_size=$puppetmaster_root_size"
params="$params;mysql_root_size=$mysql_root_size"
params="$params;managesf_root_size=$managesf_root_size"
params="$params;gerrit_root_size=$gerrit_root_size"
params="$params;redmine_root_size=$redmine_root_size"
params="$params;jenkins_root_size=$jenkins_root_size"
params="$params;slave_root_size=$slave_root_size"

params="$params;jenkins_user_pwd=$jenkins_user_pwd;jenkins_master_url=$jenkins_master_url"
params="$params;sg_admin_cidr=$sg_admin_cidr;sg_user_cidr=$sg_user_cidr"
params="$params;ext_net_uuid=$ext_net_uuid"

function get_params {
    puppetmaster_image_id=`glance image-show ${STACKNAME}_install-server-vm | grep "^| id" | awk '{print $4}'`
    params="$params;puppetmaster_image_id=$puppetmaster_image_id"
    sf_image_id=`glance image-show ${STACKNAME}_softwarefactory | grep "^| id" | awk '{print $4}'`
    params="$params;sf_image_id=$sf_image_id"
    sfconfigcontent=`cat $SFCONFIGFILE | base64 -w 0`
    params="$params;sf_config_content=$sfconfigcontent"
}

function register_images {
    for img in install-server-vm softwarefactory; do
        checksum=`glance image-show ${STACKNAME}_$img | grep checksum | awk '{print $4}'`
        if [ -z "$checksum" ]; then
            glance image-create --name ${STACKNAME}_$img --disk-format qcow2 --container-format bare \
                --progress --file $BUILT_ROLES/$img-${SF_VER}.img.qcow2
        fi
    done
}

function unregister_images {
    for img in install-server-vm softwarefactory; do
        checksum=`glance image-show ${STACKNAME}_$img | grep checksum | awk '{print $4}'`
        newchecksum=`cat $BUILT_ROLES/$img-${SF_VER}.img.qcow2.md5 | cut -d" " -f1`
        [ "$newchecksum" != "$checksum" ] && glance image-delete ${STACKNAME}_$img || true
    done
}

function delete_images {
    for img in install-server-vm softwarefactory; do
        glance image-delete ${STACKNAME}_$img || true
    done
}

function start_stack {
    get_params
    heat stack-create --template-file sf.yaml -P "$params" $STACKNAME
}

function delete_stack {
    heat stack-delete $STACKNAME
}

function restart_stack {
    set +e
    delete_stack
    while true; do
        heat stack-list | grep "$STACKNAME"
        [ "$?" != "0" ] && break
        sleep 2
    done
    set -e
    start_stack
}

function full_restart_stack {
    unregister_images
    sleep 10
    register_images
    restart_stack
}

[ -z "$1" ] && {
    echo "$0 register_images|unregister_images|start_stack|delete_stack|restart_stack|full_restart_stack"
}
[ -n "$1" ] && {
    case "$1" in
        register_images )
            register_images ;;
        unregister_images )
            unregister_images ;;
        start_stack )
            start_stack ;;
        delete_stack )
            delete_stack ;;
        delete_images )
            delete_images ;;
        restart_stack )
            restart_stack ;;
        full_restart_stack )
            full_restart_stack ;;
        * )
            echo "Not available option" ;;
    esac
}
