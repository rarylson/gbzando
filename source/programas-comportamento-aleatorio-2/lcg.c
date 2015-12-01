#define LCG_A 501
#define LCG_C 77
#define LCG_M 32

static unsigned int current_seed = 0;

// update the seed
void lcg_seed(unsigned int seed) {
    current_seed = seed;
}

// generate a random number using a linear congruential generator
unsigned int lcg_rand(void) {
    // cast the multiplication to 'long unsigned int' to avoid overflows
    current_seed = ((long unsigned int)(LCG_A * current_seed) + LCG_C) % LCG_M;
    return current_seed;
}
