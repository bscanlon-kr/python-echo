import argparse
import json
import sys

INPUT_FILE = "./output/response.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", "-c", type=str, help="Dump the results to a CSV file")
    parser.add_argument("--errors", "-e", type=bool, help="Log errors")
    parser.add_argument("--input", "-i", type=str, help="The name of the query response file to parse")
    args = parser.parse_args()

    if args.input:
       input_file = args.input
    else:
        input_file = INPUT_FILE

    #merge_continue_checkout_with_submit_checkout_for_fallout(args.errors)

    with open(input_file, 'r') as query_response_file:
        response_json = json.load(query_response_file)
        all_hits = response_json["hits"]["hits"]
        # parse_submit_order(all_hits, args.errors)
        #parse_continue_checkout_for_unavailable_items(all_hits, args.errors)
        parse_continue_checkout_for_unavailable_items(all_hits, None, args.errors)


def merge_continue_checkout_with_submit_checkout_for_fallout(print_errors):
    with open("./continue_checkout_response.json", 'r') as query_response_file:
        continue_json = json.load(query_response_file)
    with open("./submit_checkout_response.json", 'r') as query_response_file:
        submit_json = json.load(query_response_file)

    continue_records = continue_json["hits"]["hits"]
    submit_records = submit_json["hits"]["hits"]
    submits = {}
    for submit_record in submit_records:
        message_detail = submit_record["_source"]["messageDetail"]
        submits[message_detail["metaData/guid"]] = message_detail["scenarioData/orderID"]
    parse_continue_checkout_for_unavailable_items(continue_records, submits, print_errors)


def parse_submit_order_for_unavailable_cart_items(hits, print_errors):
    num_of_delivery_orders_with_unavailable_item = 0
    num_of_pickup_orders_with_unavailable_item = 0
    print("Total records: " + str(len(hits)))
    orders_with_fallout = {"pickup": [], "delivery": []}
    for hit in hits:
        record_has_fallout = False
        message_details = hit["_source"]["messageDetail"]
        try:
            delivery_service = message_details["scenarioData/deliveryService"]
        except KeyError:
            delivery_service = None
        products = []

        # Delivery orders
        if delivery_service and "store" not in delivery_service:
            try:
                for product in json.loads(message_details["scenarioData/products"]):
                    if not product["deliveryEligible"] and not product["flashSale"]:
                        products.append(product["upc"])
                        if not record_has_fallout:
                            num_of_delivery_orders_with_unavailable_item = num_of_delivery_orders_with_unavailable_item + 1
                        record_has_fallout = True
            except json.decoder.JSONDecodeError:
                # Just skip it
                if print_errors:
                    print(message_details, file=sys.stderr)
            if record_has_fallout:
                order = {message_details["scenarioData/orderID"]: products}
                orders_with_fallout["delivery"].append(order)

        # Pickup orders
        if delivery_service and "store" in delivery_service:
            try:
                for product in json.loads(message_details["scenarioData/products"]):
                    if not product["pickupEligible"] and not product["flashSale"]:
                        products.append(product["upc"])
                        if not record_has_fallout:
                            num_of_pickup_orders_with_unavailable_item = num_of_pickup_orders_with_unavailable_item + 1
                        record_has_fallout = True
            except json.decoder.JSONDecodeError:
                # Just skip it
                if print_errors:
                    print(message_details, file=sys.stderr)
            if record_has_fallout:
                order = {message_details["scenarioData/orderID"]: products}
                orders_with_fallout["pickup"].append(order)

    with open("orders_with_unavailable_items.json", 'w') as output_file:
        output_file.write(json.dumps(orders_with_fallout))
    print("Delivery orders with an unavailable delivery item: " + str(num_of_delivery_orders_with_unavailable_item))
    print("Pickup orders with an unavailable pickup item: " + str(num_of_pickup_orders_with_unavailable_item))


def parse_continue_checkout_for_unavailable_items(hits, submits, print_errors):
    fallout_examples = []
    orders_with_fallout = []
    for hit in hits:
        products = []
        message_details = hit["_source"]["messageDetail"]
        test_version = None
        try:
            tests = json.loads(message_details["metaData/abTest"])
            for test in tests:
                if test["testID"] == "f54a22":
                    test_version = test["testVersion"]
            if test_version in ["A", "B"]:
                if message_details["scenarioData/numberNotAvailableItems"] != "0.0":
                    try:
                        for product in json.loads(message_details["scenarioData/products"]):
                            reason = ""
                            fallout_in_cart = False
                            for key, value in product.items():
                                if key == "falloutReason":
                                    reason = value
                                if key == "deliveryEligible":
                                    fallout_in_cart = not value
                            if reason:
                                products.append({"upc": product["upc"], "falloutReason": reason, "wasFalloutInCart": fallout_in_cart})
                    except json.decoder.JSONDecodeError:
                        # Just skip it
                        if print_errors:
                            print(message_details, file=sys.stderr)
                    if submits:
                        if submits[message_details["metaData/guid"]] not in orders_with_fallout:
                            fallout_examples.append({
                                "userId": message_details["metaData/guid"],
                                "products": products,
                                "variant": test_version,
                                "orderId": submits[message_details["metaData/guid"]]
                            })
                            orders_with_fallout.append(submits[message_details["metaData/guid"]])
                    else:
                        fallout_examples.append({
                            "userId": message_details["metaData/guid"],
                            "products": products,
                            "variant": test_version
                        })
        except KeyError:
            if print_errors:
                print(message_details)
    with open("./fallout_examples.csv", 'w') as fallout_examples_file:
        fallout_examples_file.write("sep=;\n")
        fallout_examples_file.write("userId;variant;orderId;products\n")
        for example in fallout_examples:
            fallout_examples_file.write(example["userId"] + ";" + example["variant"] + ";" + example["orderId"] + ";" +
                                        str(example["products"]) + "\n")
    print(json.dumps(fallout_examples))


if __name__ == "__main__":
    main()
