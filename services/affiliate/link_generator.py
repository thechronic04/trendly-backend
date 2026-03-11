from typing import Optional
import os
import urllib.parse

def get_affiliate_links(product_title: str, category: str, asin: Optional[str] = None, flipkart_id: Optional[str] = None) -> dict:
    """
    Generates affiliate links for multiple networks.
    """
    links = {}
    query = urllib.parse.quote_plus(product_title)
    
    # 1. Amazon Associates
    amazon_tag = os.getenv("AMAZON_ASSOC_TAG", "trendlyai-21")
    if asin:
        links["amazon"] = f"https://www.amazon.com/dp/{asin}?tag={amazon_tag}"
    else:
        links["amazon"] = f"https://www.amazon.com/s?k={query}&tag={amazon_tag}"
    
    # 2. Flipkart Affiliate
    flipkart_id_tag = os.getenv("FLIPKART_AFFILIATE_ID", "default_id")
    if flipkart_id:
        links["flipkart"] = f"https://www.flipkart.com/p/p/{flipkart_id}?affid={flipkart_id_tag}"
    else:
        links["flipkart"] = f"https://www.flipkart.com/search?q={query}&affid={flipkart_id_tag}"
        
    # 3. CJ Affiliate (Placeholder endpoint)
    # Typically requires a specific link per product from their API
    cj_id = os.getenv("CJ_API_USER")
    if cj_id:
        links["cj"] = f"https://www.anrdoezrs.net/links/{cj_id}/search?keywords={query}"
        
    # 4. Rakuten / LinkShare (Placeholder)
    rakuten_id = os.getenv("RAKUTEN_API_KEY")
    if rakuten_id:
        links["rakuten"] = f"https://click.linksynergy.com/fs-bin/click?id={rakuten_id}&subid=0&offerid=1&type=3&tmpid=1&RD_PARM1={query}"

    # 5. ShareASale (Placeholder)
    sas_id = os.getenv("SHAREASALE_API_KEY")
    if sas_id:
        links["shareasale"] = f"https://www.shareasale.com/m-pr.cfm?merchantID=12345&userID={sas_id}&productID=67890"

    return links
