import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { ParametersService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"
import AddItem from "../../components/Parameters/AddParameter.tsx"

const itemsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/parameters")({
  component: Parameters,
  validateSearch: (search) => itemsSearchSchema.parse(search),
})

const PER_PAGE = 5

function getItemsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ParametersService.readParameters({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["parameters", { page }],
  }
}

function ParametersTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const {
    data: items,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getItemsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && items?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getItemsQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  function toDateTime(secs: number | string): string {
    let secsNum = secs
    if (typeof secs === "string") {
      secsNum = Number.parseInt(secs)
    }
    const t = new Date(Date.UTC(1970, 0, 1)) // Epoch
    t.setUTCSeconds(secsNum as number)
    return t.toUTCString()
  }

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Value</Th>
              <Th>Type</Th>
              <Th>Version</Th>
              <Th>Last Modified Date (UTC)</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {items?.data.map((item) => (
                <Tr key={item.Name} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{item.Name}</Td>
                  <Td>{item.Value}</Td>
                  <Td isTruncated maxWidth="30px">
                    {item.Type}
                  </Td>
                  <Td isTruncated maxWidth="30px">
                    {item.Version}
                  </Td>
                  <Td>{toDateTime(item.LastModifiedDate)}</Td>
                  <Td>
                    <ActionsMenu type={"Parameter"} value={item} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  )
}

function Parameters() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Parameters
      </Heading>

      <Navbar type={"Parameter"} addModalAs={AddItem} />
      <ParametersTable />
    </Container>
  )
}
