from app import main
def output_callback(s):
    print(f'{s}%')
if __name__ == "__main__":
    # import daiquiri
    # daiquiri.setup(level=daiquiri.logging.INFO)
    # logger=daiquiri.getLogger('workflow-tool')
    # from app.workflow_tool.tools import CRFCompressTool
    # tool=CRFCompressTool()
    # tool.percent_callback=output_callback
    # tool.run(r"C:\Users\jtpet\Nextcloud\Projects\Python\Distributed\ultimate_workflow_tool\tests\source.mp4",
    #             'out.mp4',{'CRF Value':21,'Codec':'x264'},threads=24)
    main()


# from app.utils import file_str
# import os
# from orderedset import OrderedSet
# from app.workflow_tool.tools import AudioInsertTool, ConvertVideoTool,ExtractAudioTool,AudioLevelTool, ToolRunException,TOOLS
# import daiquiri
# daiquiri.setup(level=daiquiri.logging.INFO)
# logger=daiquiri.getLogger('workflow-tool')
# output=None
# start_file=r"C:\Users\jtpet\Nextcloud\Projects\Python\Distributed\ultimate_workflow_tool\tests\source.mp4"
# final_output='final.mp4'
# tool_chain=(ConvertVideoTool(),ExtractAudioTool(),AudioLevelTool(),AudioInsertTool())
# options=(None,{'Track Number':1},None,{'Track Number':1,'Video File':'%Convert Video%'})

# last_output=start_file
# all_outputs={}
# tmp_files=[]
# for tool,option in zip(tool_chain,options):
#     try:
#         next_allowed_inputs=tool_chain[tool_chain.index(tool)+1].allowed_inputs
#         allowed_outputs=tool.allowed_outputs[0] if isinstance(tool.allowed_outputs[0],tuple) else tool.allowed_outputs
#         out_type=list(OrderedSet(next_allowed_inputs).intersection(tool.allowed_outputs))[0]
#     except IndexError:
#         out_type=tool.allowed_outputs[0]
#     out_name=f'__temp__{type(tool).__name__}.{out_type}'.lower().replace('tool','') if tool!=tool_chain[-1] else final_output
#     #deal with special options
#     if option:
#         for key,val in option.items():
#             for t in TOOLS:
#                 if type(val)==str and f'%{t[0]}%' in val:
#                     option[key]=all_outputs[t[1]]
#     try:
#         last_output=tool.run(last_output,out_name,option,24)
#     except ToolRunException as e:
#         logger.error(e)
#         break
#     all_outputs[type(tool)]=last_output
#     if os.path.split(last_output)[1].startswith('__temp__'):tmp_files.append(last_output)
# for f in tmp_files:
#     os.remove(f)
