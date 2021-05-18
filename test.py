import boto
import boto.emr
from boto.emr.instance_group import InstanceGroup

conn = boto.emr.connect_to_region('us-east-1')
print(conn)

instance_groups = []

instance_groups.append(InstanceGroup(
    num_instances=1,
    role="MASTER",
    type="m1.small",
    market="ON_DEMAND",
    name="Main node"))

instance_groups.append(InstanceGroup(
    num_instances=2,
    role="CORE",
    type="m1.small",
    market="ON_DEMAND",
    name="Worker nodes"))
    
# instance_groups.append(InstanceGroup(
#     num_instances=2,
#     role="TASK",
#     type="m1.small",
#     # market="SPOT",
#     name="My cheap spot nodes",
#     # bidprice="0.002"
#     ))

print(instance_groups)