///@author: Jane Doe, BlueOcean Robot & Automation, Ltd.
///@brief: ArgosX Vision System interface - setup general
///@create: 2021-12-06


function init()
{
	//updataStatus();
	setDomPath('/apps/mastering/svr_general');
	setUpdateGuideBar(updateGuideBar);
	setUpdateData(updateData);
	onReady();
	$('#play_status').val('Standby');
}


///@return		f-button infos array
function initButtonBar()
{
	console.log('initButtonBar()');	
	var btn_infos = [
		{
			label: 'Execute\nmastering',
			script: 'exeMastering();'
		 },
		 {
			label: 'Go to encoder\noffset pose',
			script: 'goEncoderofsPos();'
		 }
	]
	return btn_infos;
}


///@brief      have guidebar display message on clicking widget
function updateGuideBar()
{
	let sg = setGuideBarMsg;
	let msg_ip_addr = 'Enter the IP address of ArgosX.'
	let msg_port = 'Enter the port # of ArgosX.'
	let msg_joint = 'Enter the number of [1~6]. After change the joint number, you have to apply[shift + OK] parameter';

	sg('ip_addr', msg_ip_addr);
	sg('port', msg_port);
	sg('joint', msg_joint);
}


///@param[in]	data
///@param[in]	to_data     true; element->data, false; element<-data
function updateData(data, to_data)
{
	ddx_edit_ip(data, 'ip_addr', to_data);
	ddx_edit_i(data, 'port', to_data);
	ddx_edit_i(data, 'joint', to_data);
	//ddx_edit_i(data, 'cor_ofs', to_data);
}


function exeMastering()
{
	
	/*console.log('executeText()');
	let bret = confirm('Proceed?');
	console.log('bret='+bret);
	*/
	Interval = setInterval('updataStatus()', 1000);   
	$('#play_status').val('mastering in progress...');
	loadData(g_dom_path + '_exe');
	//$('#play_status').val('End');
}

function goEncoderofsPos()
{
	Interval = setInterval('updataStatus()', 1000);   
	$('#play_status').val('go to the offset pose...');
	loadData(g_dom_path + '_ofs_pose');
}


function updataStatus()
{
    var path = '/apps/mastering/svr_general_process_status';
	var url = domainMb()+path;

	$.get(url, function(data) {
		if (data.play_status == 'mastering end')
		{	
			clearInterval(Interval);
		}
		else if((data.play_status.charAt(0) == 'E')&(data.play_status.charAt(1) == 'R')) 
		{	
			clearInterval(Interval);
		}
		else if (data.play_status == 'reached the offset pose')
		{	
			clearInterval(Interval);
		}
		display(data);
	});
}


///@param[in]	data
///@brief		(callback function) form <- data
function display(data)
{
	console.log(data);
	$('#play_status').val(data.play_status);
	$('#cor_ofs').val(data.cor_ofs);
}


