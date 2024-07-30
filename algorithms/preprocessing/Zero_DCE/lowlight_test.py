import algorithms.preprocessing.Zero_DCE.model as model
import torch
import torch.optim
import os
import numpy as np


 
def lowlight(data_lowlight):
	os.environ['CUDA_VISIBLE_DEVICES']='0'
	data_lowlight = (np.asarray(data_lowlight)/255.0)
	data_lowlight = torch.from_numpy(data_lowlight).float()
	data_lowlight = data_lowlight.permute(2,0,1)
	data_lowlight = data_lowlight.unsqueeze(0)

	DCE_net = model.enhance_net_nopool()
	module_path = os.path.join(os.getcwd(), 'algorithms', 'preprocessing', 'Zero_DCE')
	DCE_net.load_state_dict(torch.load(f'{module_path}/snapshots/Epoch99.pth', map_location=torch.device('cpu')))
	_,enhanced_image,_ = DCE_net(data_lowlight)

	return enhanced_image
