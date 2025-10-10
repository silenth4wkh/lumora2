<?php
/**
 * Title: FAQ - AI Video
 * Slug: lumora/faq
 * Categories: lumora
 * Description: Accessible accordion FAQ with schema injection hook.
 */

$faq = [
    [
        'q' => __( 'Professzionális lesz-e az AI videó minősége?', 'lumora-ai' ),
        'a' => __( 'Igen. Díjnyertes rendezők és vágók felügyelik a produkciót. Az AI a sebességet és a skálát adja.', 'lumora-ai' ),
    ],
    [
        'q' => __( 'Milyen AI eszközöket használunk?', 'lumora-ai' ),
        'a' => __( 'Bevált in-house technológia és modern kereskedelmi eszközök kombinációja a skálázható, személyre szabott gyártáshoz.', 'lumora-ai' ),
    ],
    [
        'q' => __( 'Milyen gyors a szállítás?', 'lumora-ai' ),
        'a' => __( 'Projektfüggő, de AI-val sokszor napok alatt megoldható, ami korábban hetek voltak.', 'lumora-ai' ),
    ],
    [
        'q' => __( 'Hogyan csökkent költséget az AI?', 'lumora-ai' ),
        'a' => __( 'Automatizált posztprodukció, lokalizáció és asset generálás, így a büdzsé a kreatív ötletekre mehet.', 'lumora-ai' ),
    ],
];

// Build FAQPage schema
$schema = [
    '@context' => 'https://schema.org',
    '@type' => 'FAQPage',
    'mainEntity' => array_map( function( $item ){
        return [
            '@type' => 'Question',
            'name' => wp_strip_all_tags( $item['q'] ),
            'acceptedAnswer' => [
                '@type' => 'Answer',
                'text' => wp_kses_post( $item['a'] ),
            ],
        ];
    }, $faq ),
];

// Print JSON-LD (requires theme helper)
if ( function_exists( 'lumora_ai_print_json_ld' ) ) {
    add_action( 'wp_head', function() use ( $schema ) { lumora_ai_print_json_ld( $schema ); } );
}
?>
<!-- wp:group {"style":{"spacing":{"padding":{"top":"clamp(2rem,4vw,4rem)","bottom":"clamp(2rem,4vw,4rem)"}}},"layout":{"type":"constrained","contentSize":"900px"}} -->
<div class="wp-block-group" style="padding-top:clamp(2rem,4vw,4rem);padding-bottom:clamp(2rem,4vw,4rem)"><!-- wp:heading {"level":2} -->
<h2><?php echo esc_html__( 'GYIK', 'lumora-ai' ); ?></h2>
<!-- /wp:heading -->

<!-- wp:group {"style":{"spacing":{"blockGap":".75rem"}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group">
<?php foreach ( $faq as $idx => $item ): ?>
<!-- wp:details -->
<details>
  <summary><?php echo esc_html( $item['q'] ); ?></summary>
  <!-- wp:paragraph -->
  <p><?php echo esc_html( $item['a'] ); ?></p>
  <!-- /wp:paragraph -->
  </details>
<!-- /wp:details -->
<?php endforeach; ?>
</div>
<!-- /wp:group --></div>
<!-- /wp:group -->


