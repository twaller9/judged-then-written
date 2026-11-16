# Results summary

## llama31-8b: `own` vs `other` (n = 250 posts; crowd says at fault on 125)

- Manipulation check, `own`: reply addresses the reader as the writer in 204/250
- Manipulation check, `other`: reply addresses the reader as the writer in 32/250

Mean P(fault) by point in the reply (crowd mean 0.438):

| framing | 0% | 25% | 50% | 75% | 100% |
|---|---|---|---|---|---|
| own | 0.617 | 0.482 | 0.480 | 0.461 | 0.418 |
| other | 0.655 | 0.512 | 0.516 | 0.494 | 0.446 |

- Ownership effect before writing (own − other): -0.038 [-0.043, -0.033]
- Ownership effect after reply (own − other): -0.028 [-0.062, +0.006]
- Writing effect, `own` (after − before): -0.199 [-0.233, -0.166]
- Writing effect, `other` (after − before): -0.209 [-0.243, -0.177]
- Writing × ownership: +0.010 [-0.024, +0.044]

Agreement with the crowd majority (P(fault) ≥ 0.5 vs crowd share ≥ 0.5):

| crowd says | framing | before | after |
|---|---|---|---|
| at fault (n=125) | own | 80% | 58% |
| at fault (n=125) | other | 87% | 62% |
| not at fault (n=125) | own | 48% | 78% |
| not at fault (n=125) | other | 39% | 80% |

Copying control (verdict phrases deleted from the reply, n = 250):

- `own` P(fault) after reply: original 0.418, masked 0.507; writing effect with masking -0.110 [-0.137, -0.083]
- `other` P(fault) after reply: original 0.446, masked 0.516; writing effect with masking -0.139 [-0.166, -0.113]

## llama31-8b: `own_plain` vs `reddit_plain` (n = 250 posts; crowd says at fault on 125)

- Manipulation check, `own_plain`: reply addresses the reader as the writer in 249/250
- Manipulation check, `reddit_plain`: reply addresses the reader as the writer in 246/250

Mean P(fault) by point in the reply (crowd mean 0.438):

| framing | 0% | 25% | 100% |
|---|---|---|---|
| own_plain | 0.608 | 0.330 | 0.312 |
| reddit_plain | 0.613 | 0.323 | 0.299 |

- Ownership effect before writing (own − other): -0.005 [-0.011, +0.001]
- Ownership effect after reply (own − other): +0.013 [-0.019, +0.044]
- Writing effect, `own_plain` (after − before): -0.296 [-0.329, -0.261]
- Writing effect, `reddit_plain` (after − before): -0.314 [-0.349, -0.280]
- Writing × ownership: +0.018 [-0.013, +0.050]

Agreement with the crowd majority (P(fault) ≥ 0.5 vs crowd share ≥ 0.5):

| crowd says | framing | before | after |
|---|---|---|---|
| at fault (n=125) | own_plain | 82% | 45% |
| at fault (n=125) | reddit_plain | 82% | 45% |
| not at fault (n=125) | own_plain | 50% | 86% |
| not at fault (n=125) | reddit_plain | 45% | 90% |

## qwen25-7b: `own` vs `other` (n = 250 posts; crowd says at fault on 125)

- Manipulation check, `own`: reply addresses the reader as the writer in 231/250
- Manipulation check, `other`: reply addresses the reader as the writer in 182/250

Mean P(fault) by point in the reply (crowd mean 0.438):

| framing | 0% | 25% | 100% |
|---|---|---|---|
| own | 0.496 | 0.543 | 0.467 |
| other | 0.534 | 0.567 | 0.481 |

- Ownership effect before writing (own − other): -0.038 [-0.048, -0.026]
- Ownership effect after reply (own − other): -0.015 [-0.047, +0.019]
- Writing effect, `own` (after − before): -0.029 [-0.064, +0.006]
- Writing effect, `other` (after − before): -0.052 [-0.085, -0.020]
- Writing × ownership: +0.023 [-0.010, +0.059]

Agreement with the crowd majority (P(fault) ≥ 0.5 vs crowd share ≥ 0.5):

| crowd says | framing | before | after |
|---|---|---|---|
| at fault (n=125) | own | 38% | 38% |
| at fault (n=125) | other | 45% | 37% |
| not at fault (n=125) | own | 42% | 51% |
| not at fault (n=125) | other | 42% | 45% |
