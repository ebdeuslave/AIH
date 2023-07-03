<?php
require_once('PrestaShop-webservice-lib-master/PSWebServiceLibrary.php');

if (isset($argv)) {
    try {
        // creating webservice access
        $webService = new PrestaShopWebservice('https://' . $argv[1] . '.ma/', 'API_KEY', false);

        // get order
        $xml = $webService->get([
            'resource' => 'orders',
            'id' => $argv[2],
        ]);

        $orderFields = $xml->order->children();

        // set status to Shipped "ID:4"
        $orderFields->current_state = 4;

        // update
        $updatedXml = $webService->edit([
            'resource' => 'orders',
            'id' => (int) $orderFields->id,
            'putXml' => $xml->asXML(),
        ]);

        $orderFields = $updatedXml->orders->children();

        // print a success msg
        echo $argv[1] . '-' . $argv[2] . ' : Encours de livraison' . PHP_EOL;

    } catch (PrestaShopWebserviceException $ex) {
        // Shows a message related to the error
        echo $argv[1] . '-' . $argv[2] . ': ERROR!\n';
    }
} else {
    echo "Give me an ID";
}