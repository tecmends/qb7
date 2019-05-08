from quickbooks.objects import Invoice, SalesItemLine, SalesItemLineDetail

from invoice.customerrors import InvalidItemRef
from invoice.invoiceoperation import InvoiceOperations
import csv

from invoice.models import CsvFile, CsvFileResults


def process_invoice(row):
    # TODO read mapping here
    invoice_obj = dict()
    invoice_obj['invoicenumber'] = row['invoicenumber']
    invoice_obj['customerrefno'] = row['customerrefno']
    invoice_obj['duedate'] = row['duedate']
    invoice_obj['lines'] = list()
    return invoice_obj


def process_line(row):
    # TODO read mapping here
    line_item = dict()
    line_item['lineno'] = row['lineno']
    line_item['itemcode'] = row['itemcode']
    line_item['itemdesc'] = row['itemdesc']
    line_item['unitprice'] = row['unitprice']
    line_item['qty'] = row['qty']
    return line_item


def process_csv_rows(path):
    final_dic = {}
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            invoice_no = row['invoicenumber']
            if invoice_no not in final_dic:
                final_dic[invoice_no] = process_invoice(row)
            invoice_obj = final_dic[invoice_no]
            line = process_line(row)
            invoice_obj['lines'].append(line)
    return final_dic


def save_invoice_as_failed(csv_file, message):
    csv_file_result = CsvFileResults()
    csv_file_result.csv_file = csv_file
    csv_file_result.status = 'F'
    csv_file_result.error_message = message
    csv_file_result.save()
    csv_file_result.status = 'F'
    csv_file_result.save()


def save_invoice_as_success(csv_file, invoice_obj, io):
    query_invoice = Invoice.get(invoice_obj.Id, qb=io.client)
    csv_file_result = CsvFileResults()
    csv_file_result.csv_file = csv_file
    csv_file_result.status = 'S'
    csv_file_result.invoice_id = invoice_obj.DocNumber
    csv_file_result.customer_id = invoice_obj.CustomerRef.value
    csv_file_result.customer_name = invoice_obj.CustomerRef.name
    csv_file_result.total_amount = str(query_invoice.TotalAmt)
    csv_file_result.save()


def get_lines_item_codes(lines):
    line_item_code_list = list()
    for line in lines:
        line_item_code_list.append(line['itemcode'])
    return line_item_code_list


def create_line_obj(line_dic, codes):
    line = SalesItemLine()
    line.LineNum = line_dic['lineno']
    line.Description = line_dic['itemdesc']
    line.Amount = line_dic['unitprice']
    line.SalesItemLineDetail = SalesItemLineDetail()
    line_item_code = line_dic['itemcode']
    line.SalesItemLineDetail.ItemRef = codes[line_item_code].to_ref()
    return line


def create_invoice_obj(invoice_dic, io):
    taxcode = io.get_tax_codes()[0]
    invoice = Invoice()
    invoice.DocNumber = invoice_dic['invoicenumber']
    invoice.DueDate = invoice_dic['duedate']
    customer = io.get_customer_by_id(invoice_dic['customerrefno'])
    invoice.CustomerRef = customer.to_ref()
    # Lines
    lines = invoice_dic['lines']
    line_item_codes = get_lines_item_codes(lines)
    codes = io.get_items_from_list(line_item_codes)
    for line in lines:
        line_obj = create_line_obj(line, codes)
        line_obj.SalesItemLineDetail.TaxCodeRef = taxcode.to_ref()
        invoice.Line.append(line_obj)
    io.save_invoice(invoice)
    return invoice


def create_line_obj_for_post(validate_date, codes):
    line = SalesItemLine()

    line.LineNum = validate_date.get('line_no')
    line.Description = validate_date.get('item_description')
    line.Amount = validate_date.get('unit_price')
    line.SalesItemLineDetail = SalesItemLineDetail()
    line_item_code = validate_date.get('item_code')
    line.SalesItemLineDetail.ItemRef = codes[line_item_code].to_ref()
    line.SalesItemLineDetail.TaxCodeRef = '24'
    return line


def create_invoice_obj_for_post(validated_data, user):
    io = InvoiceOperations(user_id=user.id)

    invoice = Invoice()
    invoice.DocNumber = validated_data.get("invoice_id")
    invoice.DueDate = validated_data.get("due_date")
    customer = io.get_customer_by_id(validated_data.get('customer_ref_number'))
    invoice.CustomerRef = customer.to_ref()
    lines = validated_data.get("line_items")
    item_codes = list()
    for line in lines:
        item_codes.append(line['item_code'])
    codes = io.get_items_from_list(item_codes)
    print("codes", codes)
    if len(codes) != len(list(set(item_codes))):
        raise InvalidItemRef("Invalid item ref code")
    for line in lines:
        line_obj = create_line_obj_for_post(line, codes)
        invoice.Line.append(line_obj)
    io.save_invoice(invoice)
    return invoice


def process_csv(csv_file):
    user_id = csv_file.user.id
    io = InvoiceOperations(user_id=user_id)

    path = csv_file.upload_file.path
    invoice_dic = process_csv_rows(path)
    for key in invoice_dic.keys():
        invoice_obj = invoice_dic[key]
        print("processing invoice", invoice_obj)
        lines = invoice_obj['lines']
        customer_id = invoice_obj['customerrefno']
        if not io.do_customer_exists(customer_id):
            print("CustomerID is invalid skipping invoice")
            save_invoice_as_failed(csv_file, "Invalid customer no :{}".format(customer_id))
            continue
        line_item_code_list = list()
        for line in lines:
            line_item_code_list.append(line['itemcode'])

        if not io.are_line_item_codes_valid(line_item_code_list):
            print("Some the the line codes are invalid")
            save_invoice_as_failed(csv_file,
                                   "One of the line no are invalid :{}".format(customer_id))
            continue
        invoice = create_invoice_obj(invoice_obj, io)
        save_invoice_as_success(csv_file, invoice, io)
