from get_leader_Ethena_function import get_ethena_Data
from get_Pendle_Data import get_Pendle_Data

Ena_ytMul,Ena_unApy,Ena_impApy,Ena_feeRate,Ena_swapFee,Ena_ytRoi,Ena_expiry,Ena_priceImpact = get_Pendle_Data("0xa36b60a14a1a5247912584768c6e53e1a269a9f7","0x029d6247adb0a57138c62e3019c92d3dfc9c1840")
print(Ena_ytMul,Ena_unApy,Ena_impApy,Ena_feeRate,Ena_swapFee,Ena_ytRoi,Ena_expiry,Ena_priceImpact)
                