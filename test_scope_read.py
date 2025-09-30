import matplotlib.pyplot as plt
import numpy as np
from ds1202 import connect_to_scope, ds_1202_read_full, ds_1202_read_binary, ds_1202_decode_binary

print("connecting to scope...")
rm, scope = connect_to_scope("10.0.4.104")		#your scope ip
tdata, scope_data = ds_1202_read_full(scope, 1)
tdata2, scope_data2 = ds_1202_read_full(scope, 2)

data_ch1 = ds_1202_read_binary(scope, 1)
data_ch2 = ds_1202_read_binary(scope, 2)
td1,v1 = ds_1202_decode_binary(data_ch1)
td2,v2 = ds_1202_decode_binary(data_ch2)


fig,ax = plt.subplots()
ax.plot(tdata, scope_data, label="f1")
ax.plot(tdata2, scope_data2, label="f2")
ax.plot(td1, v1, label="r1")
ax.plot(td2, v2, label="r2")
ax.legend()
plt.show()
