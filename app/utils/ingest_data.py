from math import ceil
import os
import json
import subprocess

import pandas as pd

DOCUMENT_COLS = ['uid', 'text', 'smry_text', 'clean_text', 'keywords']


def parse_transcript(df_srt):
    out_text =""
    for _, row in df_srt.iterrows():
        out_text += " " + row['text']
    return out_text



def export_df_to_json(df, filename):
    '''
    df : the dataframe that needs to be dumped as json
    filename : string path and name of the destination json file
    '''
    df_json = df.to_dict(orient="records")
    with open(filename, 'wt') as f_out:
        json.dump(df_json, f_out, indent=2)



def load_jsonfile(filename):
    '''
    filename : filepath and filename(.json file) as a single string
    This function can be used to read any json file
    '''
    with open(filename, 'rt') as f:
        data_json = json.load(f)
    return data_json



def append_json_files(file1, file2, output_file):
    """
    This function appends the content of file2 to file1 and writes the result to output_file.
    """
    data1 = load_jsonfile(file1)
    data2 = load_jsonfile(file2)
    
    combined_data = data1 + data2
    
    with open(output_file, 'wt') as f_out:
        json.dump(combined_data, f_out, indent=2)



def create_blocks(df, block_size=5, stride=1, max_duration=120):
    '''
    Use sliding window of size 'block_size' minutes with stride of 'stride' minutes to generate text blocks.
    Generated blocks wil be limited to 'max_blocks' and can be changed depending upon the processing power.
    Default parameters allow videos of upto 2hrs. to be included.
    '''
    max_blocks = ceil(((max_duration-block_size)/stride)+1)
    max_len = ceil(max(df['start'])/60)
    df_out = pd.DataFrame()

    logs = f"INFO: video length {max_len} | block size {block_size} | stride {stride} | max blocks {max_blocks}\n"
    yield logs

    for i in range(max_blocks):
        start = i*stride
        stop = block_size + i*stride
        df_block = df[(df['start']>= 60*start) & (df['start']<= 60*stop)]
        if (i + 1) % 5 == 0 or i + 1 == max_blocks:
            logs = f"INFO: generated block {i+1} | start {start} | stop {stop} | rows combined {df_block.shape[0]}\n"
            logs += "INFO: reached max blocks limit\n"
            yield logs
        transcribed = parse_transcript(df_block)
        df_block = pd.DataFrame({'block':[i+1], 'text':[transcribed], 'start_time': [min(df_block['start'])]})
        df_out = pd.concat([df_out, df_block])
        if stop >= max_len:
            logs = f"INFO: generated block {i+1} | start {start} | stop {stop} | rows combined {df_block.shape[0]}\n"
            logs += "INFO: reached end of video\n"
            yield logs
            break
    
    df_out.reset_index(drop=True, inplace=True)
    logs = f"INFO: original data {df.shape} | block data {df_out.shape}\n"
    yield logs

    yield df_out



def llm(prompt, llm_client, llm_model):
    '''
    This function uses 'llm_model' to generate response for the provided input 'prompt' to llm.
    '''
    response = llm_client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        # temperature=0,    # remove randomness for deterministic output but not using it as it makes summary clumsy with phrases like 'you stated correctly...', 'you explained it well...' etc.
        seed=72
    )

    return response.choices[0].message.content



def generate_smry(transcript, llm_client, llm_model):
    '''
    This function takes in a 'transcript' text and generates summarized text using 'llm_model' specified.
    '''
    smrize_prompt = """As a professional editor, your task is to convert the provided YouTube transcript into a concise, well-structured summary. Follow all of below steps:
        Steps:
        - Clean the text for spelling and grammatical correctness.
        - Remove filler words such as 'uhm', 'mhm', and similar phrases.
        - Retain as many original phrases as possible for authenticity.
        - Generate a summary text that contains all the information from input TRANSCRIPT and don't use words like 'you' and 'I' in the generated summary.
        - The summary should be organized into clearly labeled sections and subsections where applicable.
        - Ensure that all key information from the input TRANSCRIPT is included in the summary.
        - Don't add any new information, don't express your opinions about the speaker and don't suggest any follow up query.
        - Do not praise the speaker or me. Just provide the summary as per above directions.
        
        TRANSCRIPT: {INPUT_TRANSCRIPT}"""

    prompt = smrize_prompt.format(INPUT_TRANSCRIPT = transcript)

    return llm(prompt, llm_client, llm_model)



def generate_smry_file(df_in, llm_client, llm_model, text_col='text'):
    '''
    Iterates through each row and generates summary column content for the text in 'text_col'.
    '''
    df = df_in.copy()
    
    for index, row in df.iterrows():
        smry_text = generate_smry(row[text_col], llm_client, llm_model)
        df.loc[index, 'smry_text'] = smry_text
    
    return df



def generate_cleantxt(transcript, llm_client, llm_model):
    '''
    This function takes in a 'transcript' text and generates summarized text using 'llm_model' specified.
    '''
    cleantxt_prompt = """As a proof reader, your task is to clean the provided YouTube transcript without omitting any information from the original text.
        The generated clean output should be grammatically correct, should not have any spelling mistakes.
        It should not have filler words such as 'uhm', 'mhm', and similar phrases that can be heard in audio but does not make any sense in written transcript.
        Retain all the original phrases for authenticity.
        Don't add any new information, don't express your opinions about the speaker and don't suggest any follow up query.
        Do not praise the speaker or me. Just provide the cleaned text as per above directions.
        
        TRANSCRIPT: {INPUT_TRANSCRIPT}"""

    prompt = cleantxt_prompt.format(INPUT_TRANSCRIPT = transcript)

    response = llm_client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        # temperature=0,    # remove randomness for deterministic output but not using it as it makes summary clumsy with phrases like 'you stated correctly...', 'you explained it well...' etc.
        seed=72
    )

    return response.choices[0].message.content



def generate_cleantxt_file(df_in, llm_client, llm_model, text_col='text'):
    '''
    Iterates through each row and generates cleaned text column for the text in 'text_col'.
    '''
    df = df_in.copy()
    
    for index, row in df.iterrows():
        clean_text = generate_cleantxt(row[text_col], llm_client, llm_model)
        df.loc[index, 'clean_text'] = clean_text
    
    return df



def generate_keywords(transcript, llm_client, llm_model):
    '''
    This function takes in original/summary/cleaned 'transcript' text and generates a list of keywords and topics using 'llm_model' specified.
    '''
    keyword_prompt = """Analyze the following YouTube video TRANSCRIPT and generate a string with comma-separated 15 to 30 keywords and topics that have been discussed in the TRANSCRIPT.
        Use original phrases from TRANSCRIPT for authenticity.

        Generated Output: "keyword1, keyword2, keyword3, ...."
        
        TRANSCRIPT: {INPUT_TRANSCRIPT}"""

    prompt = keyword_prompt.format(INPUT_TRANSCRIPT = transcript)

    response = llm_client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        # temperature=0,    # remove randomness for deterministic output but not using it as it makes summary clumsy with phrases like 'you stated correctly...', 'you explained it well...' etc.
        seed=72
    )

    return response.choices[0].message.content



def generate_kwrd_file(df_in, llm_client, llm_model, text_col='smry_text'):
    '''
    Iterates through each row and generates keyword column content for the text in 'text_col'.
    '''
    df = df_in.copy()
    
    for index, row in df.iterrows():
        keywords = generate_keywords(row[text_col], llm_client, llm_model)
        df.loc[index, 'keywords'] = keywords
    
    return df



def ingest_ytscript(video_id, tscribe_vid_data, LANG, llm_client, llm_model):
    """
    Process the video transcript for the provided video_id. Creates cleaned text, summary and keywords fields.
    
    Args:
        video_id (str): The video ID to process the transcript.
        tscribe_vid_data: path to store documents as a json file; temporary files will be stored in the same location within a 'tmp' folder.
    Returns:
        None
    """
    logs = f"INFO: extracting raw video transcript '{video_id}'...\n"
    yield logs
    command = f"python ./utils/fetch_transcript.py --video_id {video_id}"
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logs = f"INFO: stdout(fetch_transcript.py): {process.stdout.decode()}\n"
    yield logs
    logs = f"INFO/ERROR: stderr(fetch_transcript.py): {process.stderr.decode()}\n"
    yield logs
    df_srt = pd.read_csv("./app_data/raw_tscript_"+video_id+".csv")
    yt_transcribed = parse_transcript(df_srt)
    logs = f"INFO: raw transcript extracted with {len(yt_transcribed.split())} words.\n"
    yield logs

    logs = f"INFO: chunking transcript...\n"
    yield logs

    for chunking_logs_nchunks in create_blocks(df_srt):
        if isinstance(chunking_logs_nchunks, str):
            yield chunking_logs_nchunks
        else:
            df_chunks = chunking_logs_nchunks
    
    logs = f"INFO: generating summary and uid for {df_chunks.shape[0]} chunks...\n"
    yield logs
    df_blocksmry = generate_smry_file(df_chunks, llm_client, llm_model)
    df_blocksmry['uid'] = df_blocksmry.apply(lambda x: video_id + '__B' + str(x['block']) + '__S' + str(x['start_time']), axis=1)

    logs = f"INFO: generating clean text...\n"
    yield logs
    df_blocksmry_v2 = generate_cleantxt_file(df_blocksmry, llm_client, llm_model)

    logs = f"INFO: generating keywords...\n"
    yield logs
    df_blocksmry_v3 = generate_kwrd_file(df_blocksmry_v2, llm_client, llm_model, text_col='text')

    logs = f"INFO: saving json file with documents to be indexed...\n"
    yield logs
    export_df_to_json(df_blocksmry_v3[DOCUMENT_COLS], tscribe_vid_data)

    activeapp_fileloc = './app_data/'
    if os.path.exists(activeapp_fileloc+"activeapp_tscript.json"):
        append_json_files(activeapp_fileloc+"activeapp_tscript.json", tscribe_vid_data, activeapp_fileloc+"activeapp_tscript.json")
    else:
        append_json_files(activeapp_fileloc+"multi_tscribe.json", tscribe_vid_data, activeapp_fileloc+"activeapp_tscript.json")
    
    logs = f"INFO: data ingest complete and activeapp json file created.\n"
    yield logs
