<?php
/**
 * Title: CTA - Free AI Consultation
 * Slug: lumora/cta
 * Categories: lumora
 * Block Types: core/group
 * Description: Prominent CTA block with short value props.
 */
?>
<!-- wp:group {"align":"full","style":{"color":{"background":"#111111"},"spacing":{"padding":{"top":"clamp(2rem,4vw,3rem)","bottom":"clamp(2rem,4vw,3rem)"}}},"layout":{"type":"constrained","contentSize":"1200px"}} -->
<div id="consultation" class="wp-block-group alignfull has-background" style="background-color:#111111;padding-top:clamp(2rem,4vw,3rem);padding-bottom:clamp(2rem,4vw,3rem)"><!-- wp:columns -->
<div class="wp-block-columns"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:heading {"level":2} -->
<h2><?php echo esc_html__( 'Ingyenes AI videó konzultáció', 'lumora-ai' ); ?></h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><?php echo esc_html__( 'Trendek, skálázási stratégiák, élő Q&A. Nézzük meg, mit hozhat az AI a márkádnak.', 'lumora-ai' ); ?></p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:list -->
<ul><li><?php echo esc_html__( 'Friss AI video trend insight', 'lumora-ai' ); ?></li><li><?php echo esc_html__( 'Gyakorlati skálázási megoldások', 'lumora-ai' ); ?></li><li><?php echo esc_html__( 'Live Q&A tapasztalt stratéga vezetésével', 'lumora-ai' ); ?></li></ul>
<!-- /wp:list -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"right"}} -->
<div class="wp-block-buttons"><!-- wp:button {"backgroundColor":"brand","textColor":"bg","style":{"border":{"radius":"9999px"},"typography":{"fontWeight":"700"}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-bg-color has-brand-background-color has-text-color wp-element-button" style="border-radius:9999px;font-weight:700" href="#contact"><?php echo esc_html__( 'Időpont foglalása', 'lumora-ai' ); ?></a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:column --></div>
<!-- /wp:columns --></div>
<!-- /wp:group -->


