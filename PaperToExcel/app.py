import streamlit as st
import base64
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
import os
import io
import pandas as pd

os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]


llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
)


prompt1=""" 
You are an AI assistant designed to help with data entry from paper documents. Your task is to analyze images containing handwritten or printed data and convert it into a structured digital format. This will help streamline the data entry process and reduce manual effort.
You will be provided with images containing data. Your job is to carefully examine the images and extract all relevant information. Pay close attention to tables, forms, or any structured layout within the images.
Here's how to approach this task:
1. Analyze the images
2. Identify the structure of the data:
   - Look for tables, columns, rows, or any organized layout
   - Determine the number of columns and rows if applicable
   - Identify any headers or labels for the data
3. Extract the data:
   - Read and transcribe all text and numbers from the images
   - Maintain the original structure and organization of the data
   - Pay attention to any special characters, symbols, or formatting
4. Present the extracted data:
   - Use markdown tables to represent the data in a structured format
   - Include column headers if present in the original images
   - Maintain the order of columns and rows as they appear in the images
5. Handling unclear or ambiguous data:
   - If any text or numbers are unclear, use [unclear] to indicate this
   - If you're unsure about the structure or organization, provide your best interpretation and note any uncertainties
Give the structured data in markdown table format. Do not include any explanations or additional text in your output.
Remember, accuracy and maintaining the original structure of the data are crucial.
"""
prompt2=""" 
You will be given a markdown table. Your task is to convert this table into a format that can be easily inserted into an Excel file using a Python script. The output should be a list of lists, where each inner list represents a row in the Excel sheet.

Here is the markdown table:
<markdown_table>
{markdown_table}
</markdown_table>

To process this markdown table:
1. Ignore the first line (header row) of the markdown table.
2. Ignore the second line (which contains the separator dashes).
3. For each subsequent line:
   a. Split the line by the pipe character (|).
   b. Remove any leading or trailing whitespace from each cell.
   c. Ignore the first and last empty cells that result from splitting (these are the outer pipes).
4. Combine all processed rows into a list of lists.

The output should be formatted as a Python list of lists, with each inner list representing a row in the Excel sheet. Do not include any explanations or additional text in your output. Do not include new line characters in your output.

For example, if the input was:
```
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| A        | B        | C        |
| D        | E        | F        |
```

The output should be:
[["A", "B", "C"], ["D", "E", "F"]]

Now, process the given markdown table and output the result in the format described above.
"""

prompt1_template = ChatPromptTemplate.from_messages(
    [
        ("system", prompt1),
        (
            "user",
            [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{image_data}"}
                }
            ],
        ),
    ]
)
prompt2_template = PromptTemplate(
    input_variables=["markdown_table"],
    template=prompt2,
)

table_chain = LLMChain(llm=llm, prompt=prompt1_template, output_key="markdown_table")
excel_chain = LLMChain(llm=llm, prompt=prompt2_template, output_key="excel_data")

overall_chain = SequentialChain(
    chains=[table_chain, excel_chain],
    input_variables=["image_data"],
    output_variables=["markdown_table", "excel_data"],
    verbose=True
)
# Streamlit app
st.title("Paper To Excel")

uploaded_file = st.file_uploader("Choose an image...", type=["jpeg","png"])

def create_excel_file(data):
    # Convert string representation of list to actual list
    data_list = eval(data)
    
    # Create DataFrame
    df = pd.DataFrame(data_list[1:])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    return output.getvalue()

if uploaded_file is not None:

    # Process the image when the user clicks the button
    if st.button("Convert to Excel"):
        with st.spinner("Converting..."):
            # Read and encode the image
            image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
            
            # Run the chain
            output = overall_chain.invoke({"image_data": image_data})
            
            # Display results
            st.subheader("Markdown Table")
            st.markdown(output["markdown_table"])
            
            st.subheader("Excel Data")
            st.text(output["excel_data"])

            # Create Excel file
            excel_file = create_excel_file(output["excel_data"])
            
            # Provide download button
            st.download_button(
                label="Download Excel file",
                data=excel_file,
                file_name="pictureToExcel.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

