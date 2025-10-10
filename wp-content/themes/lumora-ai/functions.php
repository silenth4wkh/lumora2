<?php
/**
 * Theme setup and assets
 */

if ( ! defined( 'LUMORA_AI_VERSION' ) ) {
    define( 'LUMORA_AI_VERSION', '0.1.0' );
}

add_action( 'after_setup_theme', function () {
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'editor-styles' );
    add_theme_support( 'wp-block-styles' );
    add_theme_support( 'responsive-embeds' );
} );

add_action( 'enqueue_block_assets', function () {
    // Critical CSS for front-end only
    if ( ! is_admin() ) {
        wp_enqueue_style( 'lumora-critical', get_template_directory_uri() . '/assets/css/critical.css', [], LUMORA_AI_VERSION );
    }
} );

add_action( 'wp_enqueue_scripts', function () {
    // Main CSS (purged/minified ideally via build step)
    wp_enqueue_style( 'lumora-main', get_template_directory_uri() . '/assets/css/main.css', [ 'lumora-critical' ], LUMORA_AI_VERSION );

    // Main JS as module, deferred
    wp_enqueue_script( 'lumora-main', get_template_directory_uri() . '/assets/js/main.js', [], LUMORA_AI_VERSION, true );
    wp_script_add_data( 'lumora-main', 'type', 'module' );
    // Defer is implied for footer scripts; ensure no blocking
} );

/**
 * Register pattern categories
 */
add_action( 'init', function () {
    register_block_pattern_category( 'lumora', [ 'label' => __( 'Lumora', 'lumora-ai' ) ] );
} );

/**
 * Helper to print JSON-LD in head
 */
function lumora_ai_print_json_ld( array $data ) {
    echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . '</script>' . "\n";
}


