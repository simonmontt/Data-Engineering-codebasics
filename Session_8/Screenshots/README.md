# BuildMate Rentals — Gold Business Findings

## Purpose

The Gold star schema combines the rental-management, billing, customer,
and depot datasets into one conformed analytical model. This allows
BuildMate to answer operational and financial questions that no individual
source system can answer by itself.

## 1. Rental duration by machine type

Returned rentals were grouped by asset type and their average completed
rental duration was calculated.

The machine type with the longest average rental duration was
**[LDR]**, at **[5.24] days**, based on **[100] returned rentals**.


Currently-out rentals were excluded from this calculation because their
final durations are not yet known. Their duration remains NULL rather than
being represented incorrectly as zero.

## 2. Fleet utilisation by depot

Fleet utilisation was calculated as:

asset days used / (fleet size × 30 reporting days)

The most heavily utilised depot was **[Talegaon Depot]**, with utilisation of
**[83.8]%**. This indicates that it consumed the largest share of its
available fleet-days during the June reporting window.

The asset-days measure was clipped to the reporting window, so no rental
could contribute more than thirty days.

## 3. Revenue by payer type

Revenue was grouped by the standardised payer types: direct, contract,
corporate, and prepaid.

The highest-revenue payer type was **[direct]**, contributing
approximately **₹[16394613]** across **[220] bills**, with an average bill
of **₹[74521]**.

## 4. Revenue by depot

Billing was connected to rentals through rental_id, and rentals were then
connected to the depot dimension.

This produced the depot revenue figure that neither the billing system nor
the rental-management system could provide independently.
Total matched revenue was **₹[49,775,400.42]**, approximately **[4.98] crore**.
This reconciled exactly to the total in gold_fact_billing.

The highest-revenue depot was **[Hadapsar Depot]**, generating approximately
**₹[10785755]**.

## 5. Rental priority mix

The rental mix consisted of:

- Standard: **[681] rentals ([72.3]%)**
- Priority: **[261] rentals ([27.7]%)**

This shows the proportion of the business requiring priority handling
compared with normal rental activity.

## 6. Machines currently out

There were **175 machines currently out on site** at the reporting point.

This total reconciled exactly to the 175 blank check-in records preserved
by the null-safe Silver quality filter. A careless filter would have
silently removed all of these active rentals.

The depot with the most machines currently out was **[Chakan Depot]**, with
**[45] machines**.

## Conclusion

The conformed Gold model provides one trusted view of BuildMate's rental
operations and financial performance. It connects depot capacity, machine
activity, rental duration, customer behaviour, and billing revenue while
preserving active rentals and reconciling all totals to the cleaned Silver
layer.
