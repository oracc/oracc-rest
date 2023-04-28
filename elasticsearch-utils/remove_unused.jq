{
  project,
  lang,
  entries: [
    .entries[]
    |
    {
     headword, id, icount, xis, cf, gw,
     forms: [{n: .forms[]?.n}],
     norms: [{n: .norms[]?.n}],
     senses: [{mng: .senses[]?.mng}],
     periods: [{p: .periods[]?.p}]
    }
  ],
  instances
}
